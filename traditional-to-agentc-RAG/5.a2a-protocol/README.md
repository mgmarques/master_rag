# LangGraph + A2A --- Technical Support and Warranty Specialist

This project demonstrates two independent LangGraph agents communicating
over **Agent2Agent (A2A)**.

-   **Agent 1 --- Technical Support:** routes requests and delegates
    warranty checks.
-   **Agent 2 --- Warranty Specialist:** handles warranty requests with
    its own LangGraph workflow.
-   **A2A server:** exposes Agent 2 using an Agent Card and JSON-RPC
    `message/send`.
-   **Warranty REST API:** provides warranty information to Agent 2.

## Architecture

``` text
User
  |
  v
Technical Support LangGraph (notebook)
  |-- No warranty needed --> Direct answer
  |
  +-- Warranty needed
          | A2A message/send
          v
Warranty A2A server (port 9999)
          |
          v
Warranty Specialist LangGraph
          |
          v
Warranty REST API (port 8000)
          |
          v
A2A response --> Technical Support --> Final answer
```

## Prerequisites

You need Python, `requirements.txt`, `server.py`, `warranty_server.py`,
the Technical Support notebook, and the module
`agents_stream.warranty_specialist_agent` exporting `graph`.

Install dependencies in your project environment:

``` bash
pip install -r requirements.txt
```

Configure any environment variables required by your project (the A2A
server loads `.env`).

## Start the services in order

### Terminal 1 --- Warranty REST API (port 8000)

Open a terminal in the project directory:

``` bash
python server.py
```

Keep this terminal running.

**Alternative:** If `server.py` defines a FastAPI `app` but does not
start Uvicorn itself, use:

``` bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Use only the command appropriate to your `server.py` implementation. Its
code was not provided, so confirm the startup mechanism in that file.

### Terminal 2 --- Warranty Specialist A2A server (port 9999)

Open another terminal, using the same project environment:

``` bash
python warranty_server.py
```

This command works because `warranty_server.py` contains:

``` python
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
```

The default port is `9999`, unless `WARRANTY_AGENT_PORT` is set
differently. Keep this terminal running.

### Verify the Agent Card

Open:

http://127.0.0.1:9999/.well-known/agent-card.json

Or run:

``` bash
curl http://127.0.0.1:9999/.well-known/agent-card.json
```

You should see JSON describing the **Warranty Specialist** and its
`check_warranty` skill.

**Note:** A working Agent Card proves the A2A server is reachable, not
that the warranty REST API is healthy.

### Terminal 3 --- Technical Support notebook

Open a third terminal:

``` bash
jupyter lab
```

Open the notebook and run its cells in order. The notebook's A2A
endpoint should be:

``` python
WARRANTY_AGENT_URL = "http://127.0.0.1:9999"
```

**Keep both servers running while executing the notebook.**

## Notebook health-check cell

Add this near the beginning of the notebook:

``` python
import httpx

WARRANTY_AGENT_URL = "http://127.0.0.1:9999"

async with httpx.AsyncClient(timeout=10) as client:
    response = await client.get(
        f"{WARRANTY_AGENT_URL}/.well-known/agent-card.json"
    )
    response.raise_for_status()
    card = response.json()

print("A2A server is reachable")
print("Agent:", card["name"])
print("Skills:", [skill["name"] for skill in card["skills"]])
```

## Test A2A delegation

After defining `ask_warranty_specialist` in the notebook:

``` python
print(await ask_warranty_specialist("LAP-123"))
```

**Important compatibility warning:** The notebook uses laptop IDs such
as `LAP-123`, but the server's Agent Card describes printer IDs such as
`PRINTER-1001`. The remote specialist and REST API must support the IDs
being sent. Align the examples before running the end-to-end test.

## Test the two support routes

**Route 1 --- Direct troubleshooting**

``` python
query = "My laptop screen is black. What should I try?"
```

Expected flow:

``` text
analyze_issue --> answer_directly
```

**Route 2 --- Warranty delegation**

``` python
query = (
    "My laptop screen is black. "
    "The serial number is LAP-123. "
    "Is the repair covered by the warranty?"
)
```

Expected flow:

``` text
analyze_issue
    |
    v
delegate_warranty
    |
    | A2A
    v
Warranty Specialist server
    |
    v
Warranty Specialist graph --> Warranty REST API
    |
    | A2A response
    v
answer_with_warranty
```

The Technical Support routing is **rule-based**, using keyword matching
rather than an LLM deciding whether to delegate.

## Important: two different Warranty Specialist implementations

The notebook defines a simplified local `warranty_graph` that checks a
Python `WARRANTIES` dictionary.

The actual A2A server imports:

``` python
from agents_stream.warranty_specialist_agent import graph
```

Therefore the local notebook graph is **not automatically the same** as
the remotely hosted graph. For a coherent demo, align device IDs,
datasets, and warranty-checking behavior across the notebook, the
imported graph, and the REST API.

## Troubleshooting

  -----------------------------------------------------------------------
  Problem                             Check
  ----------------------------------- -----------------------------------
  Connection refused on port 8000     Start the warranty REST API;
                                      inspect `server.py`.

  Connection refused on port 9999     Start `warranty_server.py`; check
                                      `WARRANTY_AGENT_PORT`.

  Agent Card works, lookup fails      Check remote specialist logs and
                                      REST API connectivity.

  Unknown device ID                   Align notebook IDs with the
                                      warranty provider dataset.

  `agents_stream` import error        Verify working directory, package
                                      structure, and Python environment.

  JSON-RPC error                      Verify `message/send`, the request
                                      payload, and error response.

  Top-level `await` fails             Use a notebook supporting top-level
                                      `await` or an async entry point.
  -----------------------------------------------------------------------

## Key takeaway

**LangGraph** orchestrates each agent internally. **A2A** connects
independently deployed agents. The **REST API** is an external service
used by the Warranty Specialist.

The provided FastAPI adapter demonstrates a minimal A2A JSON-RPC
request/response flow, not the full A2A feature set (task lifecycle,
streaming, security, and more).
