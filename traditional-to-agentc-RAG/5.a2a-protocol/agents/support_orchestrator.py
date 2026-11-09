"""A2A agent #3: orchestrator that talks to the other agents over A2A."""
import json
import os
import uuid

import httpx
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph

COMPANY = "Northstar Printer Support"
SERVER = os.getenv("LANGGRAPH_URL", "http://127.0.0.1:2024").rstrip("/")
DEBUG_TRAILER = os.getenv("SUPPORT_DEBUG_TRAILER", "1") == "1"
TRAILER_MARK = "\n\n---\n[debug] "

_assistant_ids: dict[str, str] = {}


# ---------- A2A client helpers ----------
async def get_assistant_id(client: httpx.AsyncClient, graph_id: str) -> str:
    if graph_id not in _assistant_ids:
        r = await client.post(f"{SERVER}/assistants/search", json={"graph_id": graph_id, "limit": 1})
        r.raise_for_status()
        items = r.json()
        if not items:
            raise RuntimeError(f"No assistant found for graph '{graph_id}'")
        _assistant_ids[graph_id] = items[0]["assistant_id"]
    return _assistant_ids[graph_id]


def extract_text(result: dict) -> str:
    """Collect the text parts of an A2A result (artifacts first, status message as fallback)."""
    texts = []
    for art in result.get("artifacts") or []:
        for part in art.get("parts") or []:
            if part.get("kind") == "text" and part.get("text"):
                texts.append(part["text"])
    if not texts:
        msg = (result.get("status") or {}).get("message") or {}
        for part in msg.get("parts") or []:
            if part.get("kind") == "text" and part.get("text"):
                texts.append(part["text"])
    return "\n".join(texts)


async def a2a_send(graph_id: str, text: str, context_id: str | None = None) -> dict:
    """Send one A2A `message/send` request to a local agent and return `result`."""
    async with httpx.AsyncClient(timeout=120) as client:
        assistant_id = await get_assistant_id(client, graph_id)
        message = {
            "role": "user",
            "parts": [{"kind": "text", "text": text}],
            "messageId": str(uuid.uuid4()),
        }
        if context_id:
            message["contextId"] = context_id  # never resend a finished taskId
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {"message": message},
        }
        r = await client.post(
            f"{SERVER}/a2a/{assistant_id}", json=payload, headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        body = r.json()
    if "error" in body:
        raise RuntimeError(f"A2A error from {graph_id}: {body['error']}")
    return body["result"]


def split_trailer(text: str) -> tuple[str, dict]:
    """Split 'answer + [debug] k=v | k=v' into (answer, {k: v})."""
    if TRAILER_MARK not in text:
        return text, {}
    body, trailer = text.split(TRAILER_MARK, 1)
    info = {}
    for pair in trailer.split(" | "):
        if "=" in pair:
            k, v = pair.split("=", 1)
            info[k.strip()] = v.strip()
    return body, info


def content_text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict))


# ---------- Graph ----------
class SupportState(MessagesState):
    route: str
    route_reason: str
    technical_answer: str
    warranty_findings: str
    tools_used: list[str]


def caller_question(state: SupportState) -> str:
    humans = [content_text(m.content) for m in state["messages"] if m.type == "human"]
    return "\n".join(humans)


def parse_decision(raw: str) -> dict:
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s[4:] if s.startswith("json") else s
    try:
        d = json.loads(s)
        if d.get("route") not in ("technical", "warranty"):
            raise ValueError("bad route")
        return d
    except Exception:
        return {
            "route": "warranty",
            "reason": "Triage reply could not be parsed; defaulting to warranty review.",
            "technical_answer": "",
        }


async def technical_support(state: SupportState) -> dict:
    result = await a2a_send("triage_agent", caller_question(state))
    decision = parse_decision(extract_text(result))
    print(f"[orchestrator] triage_agent -> {decision['route'].upper()}: {decision.get('reason', '')}")
    return {
        "route": decision["route"],
        "route_reason": decision.get("reason", ""),
        "technical_answer": decision.get("technical_answer", ""),
        "tools_used": [],
    }


def choose_route(state: SupportState) -> str:
    return state["route"]


async def warranty_specialist(state: SupportState) -> dict:
    result = await a2a_send("warranty_agent", caller_question(state))
    findings, info = split_trailer(extract_text(result))
    tools = [t for t in info.get("tools", "").split(",") if t and t != "none"]
    print(f"[orchestrator] warranty_agent answered; tools={tools}")
    return {"warranty_findings": findings, "tools_used": tools}


def final_answer(state: SupportState) -> dict:
    if state["route"] == "technical":
        body = (state.get("technical_answer") or "").strip() or (
            "Please follow the approved troubleshooting steps and contact us if the problem persists."
        )
    else:
        body = (state.get("warranty_findings") or "").strip() or (
            "We need a support specialist to review your warranty and repair options."
        )
    draft = f"{body}\n\nThank you for calling {COMPANY}. Goodbye!"
    if DEBUG_TRAILER:
        tools = ",".join(state.get("tools_used", [])) or "none"
        draft += f"{TRAILER_MARK}route={state['route']} | tools={tools}"
    return {"messages": [AIMessage(content=draft)]}


graph = (
    StateGraph(SupportState)
    .add_node("technical_support", technical_support)
    .add_node("warranty_specialist", warranty_specialist)
    .add_node("final_answer", final_answer)
    .add_edge(START, "technical_support")
    .add_conditional_edges(
        "technical_support",
        choose_route,
        {"technical": "final_answer", "warranty": "warranty_specialist"},
    )
    .add_edge("warranty_specialist", "final_answer")
    .add_edge("final_answer", END)
    .compile()
)
