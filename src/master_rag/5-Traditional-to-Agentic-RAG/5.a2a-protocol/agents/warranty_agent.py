"""A2A agent #2: warranty specialist (owns the check_warranty tool)."""
import os

import httpx
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

BASE = os.getenv("WARRANTY_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
DEBUG_TRAILER = os.getenv("SUPPORT_DEBUG_TRAILER", "1") == "1"


@tool
async def check_warranty(device_id: str) -> dict:
    """Look up warranty coverage for a device ID using the external warranty provider."""
    device_id = device_id.strip().upper()
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{BASE}/warranty/{device_id}")
        if response.status_code == 404:
            return {
                "device_id": device_id,
                "status": "unverified",
                "error": "unknown_device",
                "message": "No warranty record found for this device.",
            }
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        return {
            "device_id": device_id,
            "status": "unavailable",
            "error": "api_unavailable",
            "detail": type(exc).__name__,
        }

model=os.getenv("OPENAI_MODEL")

if model:
    llm = ChatOpenAI(model=model, temperature=0)
else:
    llm = ChatOpenAI(model="llama3.1:8b",  base_url="http://localhost:11434/v1", api_key="olama", temperature=0)

warranty_model = llm.bind_tools([check_warranty])

SYSTEM_PROMPT = (
    "You are the warranty specialist for Northstar Printer Support. "
    "The technical agent escalated a suspected hardware failure, an unresolved "
    "issue, or an explicit warranty question. "
    "The device ID format are `PRINTER-Numbers`, `SCANNER-Numbers`, or `LAP-Numbers`. "
    "If a device ID is supplied, call check_warranty to verify its coverage; do not invent a status. "
    "If no device ID is provided, ask for it without calling the tool. "
    "A missing record is unverified, not expired. "
    "A service-unavailable result is not proof of anything: say coverage could not be checked. "
    "A covered device is not automatically eligible for free repair or replacement. "
    "Never approve or promise a replacement; human review is required. "
    "Answer as short spoken guidance for a phone call.")


async def warranty_agent_node(state: MessagesState):
    reply = await warranty_model.ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    )
    return {"messages": [reply]}


def finalize(state: MessagesState):
    """Optionally append a debug trailer so callers can see which tools ran."""
    last = state["messages"][-1]
    if not DEBUG_TRAILER:
        return {}
    tools = [m.name for m in state["messages"] if m.type == "tool"]
    trailer = f"\n\n---\n[debug] tools={','.join(tools) or 'none'}"
    return {"messages": [AIMessage(content=f"{last.content}{trailer}")]}


graph = (
    StateGraph(MessagesState)
    .add_node("warranty_agent", warranty_agent_node)
    .add_node("warranty_tool", ToolNode([check_warranty]))
    .add_node("finalize", finalize)
    .add_edge(START, "warranty_agent")
    .add_conditional_edges(
        "warranty_agent", tools_condition, {"tools": "warranty_tool", "__end__": "finalize"}
    )
    .add_edge("warranty_tool", "warranty_agent")
    .add_edge("finalize", END)
    .compile()
)
