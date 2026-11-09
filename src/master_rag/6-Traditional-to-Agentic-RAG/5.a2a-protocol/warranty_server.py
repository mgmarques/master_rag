"""
A2A server for the Warranty Specialist agent (Agent 2) in charging of calling the API
to verify warranty coverage.

Run:  python warranty_server.py
Card: http://127.0.0.1:9999/.well-known/agent-card.json

The warranty REST API (server.py, port 8000) must also be running.

# Improvements:
1. Replacing Request with JSONRPCRequest
In the original code, we used async def jsonrpc(request: Request):.

* The Problem: FastAPI/Swagger has no way of knowing what is inside that request.
               The documentation just showed "Request Body" with no fields.

* The Fix: By creating the JSONRPCRequest Pydantic model, Swagger now generates a complete interactive form.
           A developer can now see exactly that they need jsonrpc, method, params, and id.
2. Modeling the Agent Card
3. Formalizing the JSON-RPC Response
4. Removing Manual JSON Parsing
"""
import os
import uuid
import uvicorn
from dotenv import load_dotenv
# To implementing Strong Typing and Schema Definition
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Body
from langchain_core.messages import HumanMessage

load_dotenv(override=True)

from agents_stream.warranty_specialist_agent import graph  # noqa: E402

HOST = "127.0.0.1"
PORT = int(os.getenv("WARRANTY_AGENT_PORT", "9999"))

# --- Pydantic Models for Agent Card ---
"""
AGENT_CARD = {
    "protocolVersion": "0.3.0",
    "name": "Warranty Specialist",
    "description": "Verifies device warranty coverage using the warranty provider API.",
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
"""
class AgentSkill(BaseModel):
    id: str = Field(..., example="check_warranty")
    name: str = Field(..., example="Check warranty coverage")
    description: str = Field(..., example="Looks up whether a device ID is under warranty.")
    tags: List[str] = Field(default=[], example=["warranty", "printer"])
    examples: List[str] = Field(default=[], example=["Check whether PRINTER-1001 is covered."])

class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False

class AgentCard(BaseModel):
    protocolVersion: str = "0.3.0"
    name: str
    description: str
    url: str
    preferredTransport: str = "JSONRPC"
    version: str
    capabilities: AgentCapabilities
    defaultInputModes: List[str] = ["text/plain"]
    defaultOutputModes: List[str] = ["text/plain"]
    skills: List[AgentSkill]

# --- Pydantic Models for JSON-RPC ---
"""
{
    "jsonrpc": "2.0",
    "id": request_id,
    "result": {
        "kind": "message",
        "role": "agent",
        "messageId": str(uuid.uuid4()),
        "parts": [{"kind": "text", "text": answer}],
}
"""
class MessagePart(BaseModel):
    kind: str = Field(..., example="text")
    text: Optional[str] = None

class MessagePayload(BaseModel):
    parts: List[MessagePart]

class RPCParams(BaseModel):
    message: MessagePayload

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str = Field(..., example="message/send")
    params: RPCParams
    id: Optional[Union[str, int]] = None

class RPCResultPart(BaseModel):
    kind: str = "text"
    text: str

class RPCResult(BaseModel):
    kind: str = "message"
    role: str = "agent"
    messageId: str
    parts: List[RPCResultPart]

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]]
    result: Optional[RPCResult] = None
    error: Optional[Dict[str, Any]] = None

app = FastAPI(
    title="Warranty Specialist A2A Agent",
    description="Agent-to-Agent server for verifying device warranty coverage.",
    version="1.0.0"
)

# Initialize the Card using the model
AGENT_CARD_DATA = AgentCard(
    name="Warranty Specialist",
    description="Verifies device warranty coverage using the warranty provider API.",
    url=f"http://{HOST}:{PORT}/",
    version="1.0.0",
    capabilities=AgentCapabilities(),
    skills=[
        AgentSkill(
            id="check_warranty",
            name="Check warranty coverage",
            description="Looks up whether a device ID is under warranty.",
            tags=["warranty", "printer", "support"],
            examples=["Check whether PRINTER-1001 is covered for a hardware repair."],
        )
    ],
)

@app.get("/.well-known/agent-card.json", response_model=AgentCard)
@app.get("/.well-known/agent.json", response_model=AgentCard)
def get_agent_card()->AgentCard:
    """Returns the agent discovery card for A2A orchestration."""
    return AGENT_CARD_DATA


@app.post("/", response_model=JSONRPCResponse,
          response_model_exclude_none=True,
          summary="JSON-RPC Interface")
async def jsonrpc(payload: JSONRPCRequest):
    """
    Main entry point for Agent-to-Agent communication.
    Supports the 'message/send' method to interact with the Warranty Specialist.
    """

    request_id = payload.id

    # 1. Method Validation
    if payload.method != "message/send":
        return JSONRPCResponse(
            id=request_id,
            error={"code": -32601, "message": "Method not found"}
        )

    # 2. Extract text from parts
    parts = payload.params.message.parts
    text = " ".join(p.text for p in parts if p.kind == "text" and p.text).strip()

    if not text:
        return JSONRPCResponse(
            id=request_id,
            error={"code": -32602, "message": "Message must contain a text part"}
        )

    # 3. Agent Logic
    try:
        result = await graph.ainvoke({"messages": [HumanMessage(content=text)]})
        answer = result["messages"][-1].content
    except Exception as e:
        return JSONRPCResponse(
            id=request_id,
            error={"code": -32000, "message": str(e)}
        )

    # 4. Structured Response
    return JSONRPCResponse(
        id=request_id,
        result=RPCResult(
            messageId=str(uuid.uuid4()),
            parts=[RPCResultPart(text=answer)]
        )
    )


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
