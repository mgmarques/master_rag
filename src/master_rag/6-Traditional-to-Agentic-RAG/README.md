# From traditional to agentic RAG
These projects demonstrate how to build a **Retrieval-Augmented Generation (RAG) application** using vector search and 
help you understand and implement a basic RAG system step by step:
* Load and preprocess documents
* Generate embeddings
* Store vectors in a vector database
* Perform similarity search
* Augment LLM responses with retrieved context

The first two projects focus on the basic processes of RAG, the first in a simple and direct (traditional) way and the 
second with the introduction of an AI agent, followed by the implementation of the main RAG process, similarity search, 
exposed as a tool to be used by the agent conditionally. For the latter, we complemented the project by connecting 
Agents Tools through a REST API.

Having covered all the basic concepts and implementations necessary to evolve any traditional RAG into an Agentic RAG, 
we move on to tow little projects to demonstrate the concepts of multi-agents.

If your project is running entirely inside your root directory as a single application, internal nodes are 
significantly easier to manage. So our first multi-agent project is a single application.

```text
# Multi-Agent Printer Support Team
                    +-----------+           
                    | __start__ |           
                    +-----------+           
                           *                
                           *                
                +-------------------+       
                | technical_support |       
                +-------------------+       
                  ...            ...        
                ..                  ...     
              ..                       ..   
+---------------------+                  .. 
| warranty_specialist |                ..   
+---------------------+             ...     
                  ***            ...        
                     **        ..           
                       **    ..             
                   +--------------+         
                   | final_answer |         
                   +--------------+         
                           *                
                           *                
                     +---------+            
                     | __end__ |            
                     +---------+  
```

The difference between a distributed multi-agent system and internal graph nodes matters because it completely changes 
how information moves, how memory is managed, and how much engineering effort is required to keep the agents 
synchronized.

Here is a direct comparison of why this distinction is critical for your LangGraph architecture:

| Feature                        | Internal Graph Nodes (Local)                                                                                     | Distributed Multi-Agent (A2A Network)                                                                                                           |
|--------------------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **Communication Mechanism**    | **Direct memory access**. Nodes pass data locally using Python function calls and LangGraph Command() operations.| **Network protocols**. Agents talk across servers using JSON-RPC, HTTP, or SSE over the A2A standard.                                           |
| **State & Memory**             | **Single Shared State**. All nodes automatically read from and write to the same AgentState object.	             | **Isolated State**. Every agent has its own private graph state. They only know what is explicitly sent in the network payload.                 |
| **Infrastructure Scalability** | **Monolithic**. The entire graph must run on the same server, using the same Python version and dependencies.    | **Microservices**. Agents can be written in different languages, hosted on separate cloud clusters (AWS, GCP), or run on third-party platforms. |
| **Latency & Network Overhead** | **Zero**. Transfers happen instantly within the server's CPU/RAM.                                                | **Variable**. Subject to network latency, API timeouts, retry logic, and payload serialization/deserialization.                                 |

Finally, our last stage is a multi-agent system that communicates with external corporate AI assistants via the A2A 
protocol. We only need the A2A architecture if we plan to deploy our agents as completely independent network services 
that other systems can call externally. A LangGraph agents communicate over the Agent-to-Agent (A2A) protocol by 
exchanging structured messages, tasks, and state-preserving continuity identifiers.

### Understanding the Two Approaches
1. Internal Nodes (Local Composition)

When you build a multi-agent system inside a single graph (e.g., using builder.add_node("agent_1", ...)), you are 
building a local monolithic system.
* **Why it's easier**: If Agent A updates a list of messages, Agent B can instantly see it because they share the exact 
  same database checkpointer and memory space.
* **Trade-off**: If your RAG pipeline gets huge and your Agent needs specialized dependencies 
  (like CUDA for an embedding model, or older libraries), all nodes are forced to share that same heavy environment.

2. Distributed Multi-Agent (A2A)

When you transition to Agent-to-Agent (A2A), you treat your agents like separate microservices.
* **Why it's powerful**: You can have an orchestrator agent running on LangGraph Cloud, a specialized security agent 
  running inside a secure enterprise network, and a data-fetching agent running on a lightweight serverless function.
* **Trade-off**: Because they do not share memory, you must carefully map and pass identifiers like contextId 
  (to keep the conversation aligned) and strictly format your message payloads so the remote agent knows what task 
  to execute.

## Distributed Multi-Agent (A2A)
Instead of relying on a single, local shared memory space (like a standard LangGraph AgentState), the A2A protocol acts 
as an open, standardized networking layer that allows independent, distributed agents to exchange information. 

The primary components transmitted during an A2A conversation between LangGraph agents include:
1. The Core State Payload (Messages Key)

    For a LangGraph assistant deployment to accept A2A requests, your graph's state schema must contain a messages key.
   * Inbound Parts: The sender agent transmits standard text and FileParts (such as files or images).
   * Outbound Parts: The receiving agent responds with replies embedded within artifacts, utilizing specific MIME types 
     (like application/json+a2ui) to format generative user interfaces or adaptive cards.  

2. Conversational Continuity Identifiers

    To maintain thread state over standard stateless network endpoints (like JSON-RPC, HTTP, or Server-Sent Events), 
    A2A payload transmissions include two vital identifiers: 
    * contextId: Functions exactly like a session or thread ID. It groups independent messages into a single, 
      cohesive conversation history.
    * taskId: Identifies the specific task or unique request/turn currently executing within that multi-agent 
      conversation thread. 

3. Tool Execution and UI Data (A2UI)

    When agents collaborate, they don't just send text; they coordinate capabilities.

    When an agent requests assistance from another, it passes down:
    * Tool-result DataParts: Executed tool call definitions and their outputs (tool_results) are passed back and forth 
      to support advanced multi-turn tasks.
    * response_schema: Structuring interrupt artifacts if an agent requires explicit user validation or confirmation 
      before proceeding. 

### Why this matters:
The A2A layer ensures that regardless of where the agents are running, they can interpret the state, track the 
conversation ID, and return clean tool results.

By communicating via A2A on LangGraph's Agent Server, an orchestration agent (e.g., a primary support agent) can 
seamlessly route queries to specialized sub-agents hosted on entirely different clusters or frameworks 
(such as Microsoft Foundry, Google ADK, or CrewAI). 

### References:
* [Langsmith A2A endpoint in Agent Server](https://docs.langchain.com/langsmith/server-a2a)
* [Building A2A Agents with LangGraph and watsonx.ai](https://heidloff.net/article/a2a-langgraph-watsonx-ai/), 
* [LangGraph & A2A: Simulating Multi-Agent AI Collaboration for Developers](https://medium.com/@onurpolat711/langgraph-a2a-simulating-multi-agent-ai-collaboration-for-developers-ca4a26f9bbe3)
* [Agent-to-Agent Communication: Connecting Foundry and LangGraph Agents via A2A](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/agent-to-agent-communication-connecting-foundry-and-langgraph-agents-via-a2a/4531378) 
* [GuiHub: A2A Multi-Agent System](https://github.com/maeste/multi-agent-a2a) 
* [Command: A new tool for building multi-agent architectures in LangGraph](https://www.langchain.com/blog/command-a-new-tool-for-multi-agent-architectures-in-langgraph)
