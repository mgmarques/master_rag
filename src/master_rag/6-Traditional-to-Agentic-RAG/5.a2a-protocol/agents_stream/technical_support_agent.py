"""A2A agent 1: first-line technical support (triage + phone guidance)."""
import os
from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import StreamWriter
from pydantic import BaseModel, Field

COMPANY = "Northstar Printer Support"

_guidance = Path(__file__).resolve().parent.parent / "support_guidance.txt"
SUPPORT_GUIDANCE = (
    _guidance.read_text(encoding="utf-8") if _guidance.exists() else "No guidance file found."
)

model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0)


class TriageDecision(BaseModel):
    route: Literal["technical", "warranty"] = Field(
        description="technical if safe approved phone guidance suffices; otherwise warranty"
    )
    reason: str = Field(description="Short explanation of why this route was selected.")


triage_model = model.with_structured_output(TriageDecision)

TRIAGE_PROMPT = f"""You are the FIRST support agent at {COMPANY}.
Decide whether you can handle the caller's request by phone or must escalate it to
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
"""

GUIDANCE_PROMPT = f"""You are the technical support agent at {COMPANY}, speaking to a caller by phone.
Use ONLY this approved policy:
{SUPPORT_GUIDANCE}

Give concise, friendly, step-by-step spoken guidance for the caller's problem.
Do not mention warranty status and do not call any tool. Do not say the problem is
definitely fixed: ask the caller to try the steps and call back if the issue persists.
"""


class TechState(MessagesState):
    route: str
    reason: str


async def triage(state: TechState, writer: StreamWriter):
    decision = await triage_model.ainvoke(
        [SystemMessage(content=TRIAGE_PROMPT), *state["messages"]]
    )
    writer({"event": "triage", "route": decision.route, "reason": decision.reason})
    return {"route": decision.route, "reason": decision.reason}


def route_after_triage(state: TechState) -> str:
    return "phone_guidance" if state["route"] == "technical" else "escalate"


async def phone_guidance(state: TechState):
    reply = await model.ainvoke([SystemMessage(content=GUIDANCE_PROMPT), *state["messages"]])
    return {"messages": [reply]}


async def escalate(state: TechState, writer: StreamWriter):
    writer({"event": "escalate", "reason": state["reason"]})
    return {"messages": [AIMessage(content=f"ESCALATE_TO_WARRANTY: {state['reason']}")]}


graph = (
    StateGraph(TechState)
    .add_node("triage", triage)
    .add_node("phone_guidance", phone_guidance)
    .add_node("escalate", escalate)
    .add_edge(START, "triage")
    .add_conditional_edges(
        "triage",
        route_after_triage,
        {"phone_guidance": "phone_guidance", "escalate": "escalate"},
    )
    .add_edge("phone_guidance", END)
    .add_edge("escalate", END)
    .compile()
)
