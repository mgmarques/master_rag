# Project : Agentic Workflow** using LangGraph 
Unlike a simple chain (which goes A $\rightarrow$ B $\rightarrow$ C), an Agentic workflow is a **loop**. The LLM is given "tools" (like a web search) and is allowed to decide for itself: *"Do I know the answer, or do I need to use a tool first?"*

Here is the step-by-step breakdown:

### 1. The "Brain" and the "Hands" (LLM & Tools)
*   **The Hands (Tools):** The code uses `TavilySearchResults`. This is a specialized search engine for LLMs that returns clean, concise results from the web.
*   **The Brain (LLM):** It uses `ChatOpenAI`, but redirects the `base_url` to **Ollama** (`localhost:11434`). This means it's running a local model (like `gemma4:12b`) but using the OpenAI-style communication protocol.
*   **Binding:** `llm.bind_tools(tools)` is the most important line here. It tells the LLM: *"Here is a list of tools you are allowed to use. If you need them, don't just guess the answer—request to use the tool."*

### 2. The State (Memory)
The code uses `MessagesState`. In LangGraph, the **State** is a shared database that all nodes in the graph can read from and write to. 
*   In this case, the state is simply a list of messages: `[HumanMessage, AIMessage, ToolMessage, ...]`.
*   Every time a node runs, it appends a new message to this list.

### 3. The Graph Logic (The Workflow)
The agent is defined as a **StateGraph**. Think of this as a flowchart.

#### The Nodes (The "Workstations")
*   **`agent` node (`call_model`)**: The LLM looks at the current messages and decides what to do. It either returns a final answer or a "tool call" (a request to search the web).
*   **`tools` node (`tool_node`)**: If the LLM requested a tool, this node actually executes the Tavily search and returns the results back to the state.

#### The Edges (The "Paths")
*   **Entry Point**: The graph always starts at the `agent`.
*   **Conditional Edge (`should_continue`)**: This is the "Decision Diamond" in the flowchart. 
    *   If the LLM's last message contains `tool_calls`, the path goes to the **`tools`** node.
    *   If the LLM just replied with text, the path goes to **`END`**.
*   **Normal Edge**: After the `tools` node finishes, the path **always** goes back to the `agent`. This allows the LLM to read the search results and decide if it has enough info to answer or if it needs to search again.

### 4. Persistence (MemorySaver)
The `MemorySaver` checkpointer allows the agent to have a **long-term memory**. 
*   When calling `app.invoke`, the code passes a `thread_id: 42`. 
*   LangGraph saves the state of the conversation for "Thread 42". If you call the function again with the same ID, the agent will remember what you talked about previously.

### Summary of the Execution Loop
1.  **Input:** User asks: *"What is the weather in SF?"*
2.  **Agent Node:** LLM realizes it doesn't know the current weather $\rightarrow$ emits a `tool_call` for Tavily.
3.  **Decision:** `should_continue` sees the tool call $\rightarrow$ routes to **`tools`**.
4.  **Tools Node:** Tavily searches the web $\rightarrow$ returns *"Sunny, 72°F in San Francisco."*
5.  **Loop Back:** Path goes back to **`agent`**.
6.  **Agent Node:** LLM reads the search result $\rightarrow$ emits a final text answer: *"The weather in SF is currently sunny and 72°F."*
7.  **Decision:** `should_continue` sees no tool call $\rightarrow$ routes to **`END`**.
8.  **Output:** User receives the final answer.

### Visual Flow
`START` $\rightarrow$ `agent` $\rightarrow$ (Does it need a tool?) 
$\rightarrow$ **Yes** $\rightarrow$ `tools` $\rightarrow$ `agent` $\rightarrow$ (Loop repeats)
$\rightarrow$ **No** $\rightarrow$ `END`
