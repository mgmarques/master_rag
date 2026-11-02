import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool

load_dotenv(override=True)

model = os.getenv("OPENAI_MODEL", "llama3.1:8b")

BASE = os.getenv("WARRANTY_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
COMPANY = "Northstar Printer Support"

llm = ChatOpenAI(
    model=model,  # "tencent/hy3:free",  "gpt-4.1-mini"
    base_url="http://localhost:11434/v1",  # "https://openrouter.ai/api/v1",
    api_key="olama",  # os.getenv("OPENROUTER_API_KEY"),
    temperature=0)

# Load technical support guidance from an external text file
GUIDANCE_FILE = Path("../../traditional-to-agentc-RAG/support_guidance.txt")

SUPPORT_GUIDANCE = GUIDANCE_FILE.read_text(encoding="utf-8")

# ---------------------- Exposed Endpoint as a Tool ----------------------
@tool
def check_warranty(device_id: str) -> dict:
    """
    Look up warranty coverage for a device ID using the external warranty provider.

    The warranty provider exposes one business endpoint: `GET /warranty/{device_id}`.

    Used by:
        Only the warranty specialist will receive this tool.
        The technical-support agent will not be bound to it.

    Returns:
        Its response calculates `covered` from the expiry date.
        HTTP 404 means no record was found—not proof that the warranty expired.
    """
    device_id = device_id.strip().upper()
    try:
        response = requests.get(f"{BASE}/warranty/{device_id}", timeout=5)
        if response.status_code == 404:
            return {
                "device_id": device_id,
                "status": "unverified",
                "error": "unknown_device",
                "message": "No warranty record found for this device.",
            }
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {
            "device_id": device_id,
            "status": "unavailable",
            "error": "api_unavailable",
            "detail": type(exc).__name__,
        }

# ---------------------- First Agent Routing Decision ----------------------
# A structured response keeps routing separate from the wording of the answer.
class TriageDecision(BaseModel):
    route: Literal["technical", "warranty"] = Field(
        description="technical if safe approved phone guidance suffices; otherwise warranty"
    )
    reason: str = Field(description="Short explanation of why this route was selected.")
    technical_answer: str = Field(
        description="Phone troubleshooting response for the technical route; empty for warranty."
    )

# The first agent makes the routing decision and drafts an answer for the technical-only path.
triage_model = llm.with_structured_output(TriageDecision)

TRIAGE_PROMPT = f"""You are the FIRST support agent at {COMPANY}.
Decide whether you can handle the caller's request by phone or must send it to
the warranty specialist.

Use ONLY this support policy:
{SUPPORT_GUIDANCE}

Routing rules, in priority order:
1. Explicit coverage/replacement requests, known hardware failure codes E500/E900,
   printer stopped working or not powering on, unresolved attempts, and unknown
   error codes -> route='warranty'.
2. E102, E205, and ordinary connection problems with approved safe phone steps,
   and no sign of failure or unresolved attempts -> route='technical'.
3. If the problem cannot be confidently solved using the approved guidance,
   default to route='warranty'.

For route='technical', write helpful concise step-by-step spoken guidance.
Do not mention warranty status or call any API. Do not say the problem is definitely
fixed: ask the customer to try the steps and call back if the issue persists.

For route='warranty', do not answer or ask anything, leave technical_answer empty.
If the original message inform the device ID pass it to the warranty.
The device ID format are `PRINTER-Numbers`, or `SCANNER-Numbers`.
Do not request warranty checks for straightforward phone-solvable problems.
"""

# ---------------------- Warranty specialist's graph with tool calling ----------------------
"""
 The warranty specialist is activated only after the technical agent chooses the warranty route. 
 It must use `check_warranty` for coverage questions with a device ID, and it must distinguish: 
 expired, covered, unverified, and service unavailable.
"""
warranty_model = llm.bind_tools([check_warranty])

def warranty_agent_node(state: MessagesState):
    reply = warranty_model.invoke([
        SystemMessage(content=(
            "You are the warranty specialist for Northstar Printer Support. "
            "The technical agent escalated a suspected hardware failure, an unresolved "
            "issue, or an explicit warranty question. "
            "The device ID format are `PRINTER-Numbers`, or `SCANNER-Numbers`."
            "If a device ID is supplied, call check_warranty to verify its coverage; do not invent a status. "
            "If no device ID is provided, ask for it without calling the tool. "
            "A missing record is unverified, not expired. "
            "A covered device is not automatically eligible for free repair or replacement. "
            "Never approve or promise a replacement; human review is required."
        )),
        *state["messages"],
    ])
    return {"messages": [reply]}

warranty_builder = StateGraph(MessagesState)
warranty_builder.add_node("warranty_agent", warranty_agent_node)
warranty_builder.add_node("warranty_tool", ToolNode([check_warranty]))
warranty_builder.add_edge(START, "warranty_agent")
warranty_builder.add_conditional_edges(
    "warranty_agent",
    tools_condition,
    {"tools": "warranty_tool", "__end__": END},
)
warranty_builder.add_edge("warranty_tool", "warranty_agent")
warranty_graph = warranty_builder.compile()

# ---------------------- Multi-agent graph ----------------------
class SupportState(TypedDict, total=False):
    question: str
    route: Literal["technical", "warranty"]
    route_reason: str
    technical_answer: str
    warranty_findings: str
    tools_used: list[str]
    draft: str

def technical_support(state: SupportState) -> dict:
    decision = triage_model.invoke([
        SystemMessage(content=TRIAGE_PROMPT),
        HumanMessage(content=state["question"]),
    ])
    print(f"TECHNICAL AGENT → {decision.route.upper()}: {decision.reason}")
    return {
        "route": decision.route,
        "route_reason": decision.reason,
        "technical_answer": decision.technical_answer,
        "tools_used": [],
    }

def choose_route(state: SupportState) -> str:
    print("Route to: ", state["route"])
    return state["route"]

def warranty_specialist(state: SupportState) -> dict:
    result = warranty_graph.invoke(
        {"messages": [HumanMessage(content=state["question"])]},
        config={"recursion_limit": 10},
    )
    tools = [m.name for m in result["messages"] if m.type == "tool"]
    print("Warranty specialist to: ", {
        "warranty_findings": result["messages"][-1].content,
        "tools_used": tools,
    })
    return {
        "warranty_findings": result["messages"][-1].content,
        "tools_used": tools,
    }

def final_answer(state: SupportState) -> dict:
    if state["route"] == "technical":
        body = state.get("technical_answer", "").strip()
        if not body:
            body = "Please follow the approved troubleshooting steps and contact us if the problem persists."
    else:
        body = state.get("warranty_findings", "").strip()
        if not body:
            body = "We need a support specialist to review your warranty and repair options."

    # Shared closing: no additional model call or API request.
    closing = f"Thank you for calling {COMPANY}. Goodbye!"
    return {"draft": f"{body}\n\n{closing}"}

"""
 There is no fixed path through both specialists. The first agent decides which path is appropriate.
 - Technical path: `START → technical_support → final_answer → END` (no warranty API request).
 - Warranty path: `START → technical_support → warranty_specialist → final_answer → END`.

 The final-answer node closes the call in both cases with a courteous sign-off.
"""
builder = StateGraph(SupportState)
builder.add_node("technical_support", technical_support)
builder.add_node("warranty_specialist", warranty_specialist)
builder.add_node("final_answer", final_answer)

builder.add_edge(START, "technical_support")
builder.add_conditional_edges(
    "technical_support",
    choose_route,
    {"technical": "final_answer", "warranty": "warranty_specialist"},
)
builder.add_edge("warranty_specialist", "final_answer")
builder.add_edge("final_answer", END)

graph = builder.compile()

if __name__ == "__main__":
    # ---------------------- Demonstrate multiple customer calls ----------------------
    """
     Compare the chosen route and the warranty tools actually executed. 
     - For E102, E205, and a basic connection problem, expect `tools_used=[]`. 
     - For suspected hardware failures or explicit warranty requests with a device ID, expect `check_warranty`.
    
     Model routing is probabilistic; inspect the actual output rather than treating every expected route as guaranteed.
    """

    examples = [
        ("Phone fix — paper jam", "My PRINTER-1001 displays error E102. What should I do?"),
        ("Phone fix — firmware", "My PRINTER-1001 shows E205. Can you help me over the phone?"),
        ("Phone fix — connection", "My PRINTER-1001 cannot connect to Wi-Fi. What can I try?"),
        ("Hardware failure — print engine", "My PRINTER-1001 shows E500. Is it covered for repair?"),
        ("Hardware failure — power", "PRINTER-2001 shows E900 and will not start."),
        ("Default failure", "My PRINTER-1001 has stopped working completely."),
        ("Unresolved phone fix", "PRINTER-1001 still shows E102 after I cleared the jam and restarted twice."),
        ("Unknown error code", "My SCANNER-3001 displays E777. Can you help?"),
        ("Explicit coverage question", "Is SCANNER-3001 still under warranty?"),
        ("Unknown device", "UNKNOWN-9999 is broken. Is its warranty active?"),
    ]

    demo_results = []
    for label, question in examples:
        print("\n" + "=" * 75)
        print("DEMO:", label)
        print("CUSTOMER:", question)
        result = graph.invoke({"question": question})
        demo_results.append((label, result))
        print("ROUTE:", result["route"])
        print("WARRANTY TOOLS USED:", result.get("tools_used", []))
        print("FINAL ANSWER:\n", result["draft"])

    print("-"*60)
    print("\nSummary Trace:")
    for label, result in demo_results:
        print(
            f"{label:34} route={result['route']:9} "
            f"tools={result.get('tools_used', [])}"
        )

    print("\nTechnical-only examples (first three):")
    for label, result in demo_results[:3]:
        print(label, "→", "PASS" if result["route"] == "technical"
                                    and not result.get("tools_used") else "REVIEW ROUTING")