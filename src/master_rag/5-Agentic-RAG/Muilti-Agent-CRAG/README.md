# Project : Muilt-Agent-CRAG 
Corrective RAG enhances the traditional RA pipeline by introducing a retrieval evaluator to assess the relationship between the retrieved documents and the query. 

This code implements what is known as **Self-Corrective RAG (Retrieval-Augmented Generation)**. 

While a basic RAG pipeline simply does `Retrieve` $\rightarrow$ `Generate`, this agentic version adds a **Quality Control** step. It evaluates the documents it finds and decides if it needs to search the web or rewrite the question to get a better answer.

### 1. The State (`GraphState`)
The `GraphState` is a `TypedDict` that acts as the "short-term memory" for the graph. Every node in the graph reads from this state and writes updates to it.
*   `question`: The user's input.
*   `generation`: The final answer produced by the LLM.
*   `web_search`: A flag (`Yes`/`No`) indicating if the internal documents were insufficient.
*   `documents`: A list of text chunks retrieved from the database or web.

### 2. The Nodes (The "Workstations")
Each node is a Python function that performs one specific task:
1.  **`retrieve_documents`**: Uses a `retriever` (likely a Vector Database like ChromaDB or Pinecone) to find documents related to the question.
2.  **`grade_documents`**: **This is the "Intelligence" step.** It uses an LLM (`assess_retrieved_docs`) to check if the documents actually answer the question. 
    *   If docs are relevant $\rightarrow$ they are kept.
    *   If docs are irrelevant $\rightarrow$ it sets `web_search = "Yes"`.
3.  **`rewrite_query`**: If the initial retrieval failed, the LLM tries to rephrase the user's question into a better version that a search engine would understand more easily.
4.  **`web_search_node`**: Takes the (possibly rewritten) question and searches the internet to find missing information.
5.  **`generation_answer`**: The final step. It takes all the gathered documents (local + web) and the original question to write a final, polished answer.

### 3. The Edges (The "Decision Logic")
The edges determine the path the data takes through the graph.

*   **Sequential Edges**: `retrieve_documents` $\rightarrow$ `grade_documents`. This always happens.
*   **Conditional Edge (`decide_to_search_the_web`)**: After grading the documents, the graph asks: *"Do we have enough info?"*
    *   If `web_search == "Yes"` $\rightarrow$ Go to **`web_search_node`**.
    *   If `web_search == "No"` $\rightarrow$ Go to **`rewrite_query`** (to optimize the prompt before generating).
*   **Final Convergence**: Both the `web_search_node` and the `rewrite_query` node lead to the `generate` node.

### 4. Visual Flow Summary
**User Question** $\rightarrow$ **Retrieve Local Docs** $\rightarrow$ **Grade Docs**
$\downarrow$
**Is it relevant?**
$\swarrow$ $\searrow$
**No (Web Search Needed)** $\quad$ **Yes (or Rewrite Needed)**
$\downarrow$ $\quad \downarrow$
**Search the Web** $\quad$ **Rewrite Question**
$\searrow$ $\swarrow$
**Generate Final Answer** $\rightarrow$ **Output**


### Key Technical Observations
1.  **Self-Correction:** This prevents the LLM from "hallucinating" an answer based on irrelevant documents. If the retriever brings back "garbage," the agent recognizes it and goes to the web instead.
2.  **Modular Design:** Because it uses LangGraph, you can easily add a new node (e.g., a "Fact Checker" node) at the end of the graph without rewriting the whole pipeline.
3.  **Logging:** The use of `Fore.MAGENTA`, `Fore.CYAN`, etc., from `colorama` allows the developer to see exactly which node is currently executing in the terminal.
