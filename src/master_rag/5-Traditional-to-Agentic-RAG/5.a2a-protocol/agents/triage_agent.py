"""A2A agent #1: first-line technical support / triage."""
import os
from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

COMPANY = "Northstar Printer Support"

_guidance = Path(__file__).resolve().parent.parent / "support_guidance.txt"
SUPPORT_GUIDANCE = (
    _guidance.read_text(encoding="utf-8") if _guidance.exists() else "No guidance file found."
)

model=os.getenv("OPENAI_MODEL")

if model:
    llm = ChatOpenAI(model=model, temperature=0)
else:
    llm = ChatOpenAI(model="llama3.1:8b",  base_url="http://localhost:11434/v1", api_key="olama", temperature=0)

class TriageDecision(BaseModel):
    route: Literal["technical", "warranty"] = Field(
        description="technical if safe approved phone guidance suffices; otherwise warranty"
    )
    reason: str = Field(description="Short explanation of why this route was selected.")
    technical_answer: str = Field(
        description="Phone troubleshooting response for the technical route; empty for warranty."
    )


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
The device ID format are `PRINTER-Numbers`, `SCANNER-Numbers`, or `LAP-Numbers`.
Do not request warranty checks for straightforward phone-solvable problems.
"""


async def triage(state: MessagesState):
    decision = await triage_model.ainvoke(
        [SystemMessage(content=TRIAGE_PROMPT), *state["messages"]]
    )
    # An A2A agent replies with text: we return the decision as a JSON string.
    return {"messages": [AIMessage(content=decision.model_dump_json())]}

graph = (
    StateGraph(MessagesState)
    .add_node("triage", triage)
    .add_edge(START, "triage")
    .add_edge("triage", END)
    .compile()
)
