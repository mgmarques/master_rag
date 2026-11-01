"""
A2A server for the Warranty Specialist agent (Agent 2) in charging of calling the API
to verify warranty coverage.

Run:  python warranty_server.py
Card: http://127.0.0.1:9999/.well-known/agent-card.json

The warranty REST API (server.py, port 8000) must also be running.
"""
import os
import uuid
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

load_dotenv(override=True)

from agents_stream.warranty_specialist_agent import graph  # noqa: E402

HOST = "127.0.0.1"
PORT = int(os.getenv("WARRANTY_AGENT_PORT", "9999"))

app = FastAPI(title="Warranty Specialist A2A Agent")

AGENT_CARD = {
    "protocolVersion": "0.3.0",
    "name": "Warranty Specialist",
    "description": "Verifies printer/device warranty coverage using the warranty provider API.",
    "url": f"http://{HOST}:{PORT}/",
    "preferredTransport": "JSONRPC",
    "version": "1.0.0",
    "capabilities": {"streaming": False, "pushNotifications": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "check_warranty",
            "name": "Check warranty coverage",
            "description": "Looks up whether a device ID is under warranty.",
            "tags": ["warranty", "printer", "support"],
            "examples": ["Check whether PRINTER-1001 is covered for a hardware repair."],
        }
    ],
}


@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/agent.json")
def agent_card():
    return AGENT_CARD


def _rpc_error(request_id, code: int, message: str):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


@app.post("/")
async def jsonrpc(request: Request):
    try:
        body = await request.json()
    except ValueError:
        return _rpc_error(None, -32700, "Parse error")

    request_id = body.get("id")
    if body.get("method") != "message/send":
        return _rpc_error(request_id, -32601, "Method not found")

    parts = body.get("params", {}).get("message", {}).get("parts", [])
    text = " ".join(p.get("text", "") for p in parts if p.get("kind") == "text").strip()
    if not text:
        return _rpc_error(request_id, -32602, "Message must contain a text part")

    result = await graph.ainvoke({"messages": [HumanMessage(content=text)]})
    answer = result["messages"][-1].content

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "kind": "message",
            "role": "agent",
            "messageId": str(uuid.uuid4()),
            "parts": [{"kind": "text", "text": answer}],
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
