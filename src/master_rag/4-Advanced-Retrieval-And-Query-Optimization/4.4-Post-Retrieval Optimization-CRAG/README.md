# Project : Advanced RAG - Corrective RAG (CRAG)
**Corrective RAG (CRAG)** is a sophisticated RAG architecture designed to solve the "hallucination" problem caused by **irrelevant retrieval**.

In standard RAG, the system assumes that whatever the retriever finds is useful. If the retriever returns "noise" (documents that look similar mathematically but are factually irrelevant), the LLM will often try to force an answer using that bad information, leading to a hallucination.

CRAG introduces a **self-correction cycle** that assesses the quality of retrieved documents; if they are of low quality, they are discarded, and the system triggers external knowledge searches to correct or supplement irrelevant or insufficient information.

An LLM can be used as an evaluator.

## Main Libraries:
- **[chromaDB](https://python.langchain.com/v0.2/docs/integrations/vectorstores/chroma/)**: Chroma is a AI-native open-source vector database focused on developer productivity
- **[Tavily Search API](https://app.tavily.com/documentation/apis)**: Tavily's Search API is a search engine built specifically for AI agents (LLMs), delivering real-time, accurate, and factual results at speed.

### The CRAG Workflow
CRAG transforms the linear RAG pipeline into a decision-making graph.

#### 1. Retrieval
The system retrieves documents from the vector database, just like standard RAG.

#### 2. Evaluation (The "Grader")
Instead of passing these documents directly to the LLM, a **Lightweight LLM (the Grader)** examines each document and the query. It assigns a label to each document:
*   **Correct:** The document is definitely relevant to the query.
*   **Incorrect:** The document is irrelevant.
*   **Ambiguous:** The document might be relevant, but it's not clear.

#### 3. Actionable Decision (The Correction Step)
Depending on the grades, CRAG takes one of three paths:

*   **Path A: All Correct $\rightarrow$ Generate**
    *   If all retrieved documents are "Correct," the system proceeds to generate the answer normally.
*   **Path B: Some Correct / Some Incorrect $\rightarrow$ Refine & Supplement**
    *   The system throws away the "Incorrect" documents.
    *   It keeps the "Correct" ones.
    *   Because the retrieval was only partially successful, it triggers a **Knowledge Retrieval (usually a Web Search)** to fill in the missing gaps.
*   **Path C: All Incorrect $\rightarrow$ Complete Pivot**
    *   The system realizes the vector database has failed completely.
    *   It ignores the retrieved documents entirely and relies solely on a **Web Search (e.g., Tavily or Google Search)** to find the answer.

#### 4. Final Generation
The LLM receives the refined context (only the "Correct" docs + the newly searched web data) and generates a factual response.

### Conceptual Implementation (Logic Flow)
CRAG is typically implemented using **LangGraph** because it requires a loop/conditional logic rather than a straight chain.

```python
# High-level logic for a CRAG node
def grade_documents(query, docs):
    # LLM Prompt: "Is this document relevant to the query? Answer YES or NO"
    grades = llm_grader.invoke(query, docs) 
    return grades

def rag_correction_loop(query):
    docs = retriever.invoke(query)
    grades = grade_documents(query, docs)
    
    filtered_docs = [doc for doc, grade in zip(docs, grades) if grade == "YES"]
    
    if len(filtered_docs) == len(docs):
        return generate_answer(query, filtered_docs) # Path A
    
    elif len(filtered_docs) > 0:
        # Path B: Some are good, but we need more
        web_results = web_search.invoke(query)
        return generate_answer(query, filtered_docs + web_results)
        
    else:
        # Path C: Total failure, go to web
        web_results = web_search.invoke(query)
        return generate_answer(query, web_results)
```

### Comparison: Standard RAG vs. RAG-Fusion vs. Corrective RAG
| Feature | Standard RAG | RAG-Fusion | Corrective RAG (CRAG) |
| :--- | :--- | :--- | :--- |
| **Core Philosophy** | "Retrieve and Generate" | "Retrieve from multiple angles" | "Retrieve, Verify, then Generate" |
| **Primary Goal** | Speed & Simplicity | Increase Recall (find more) | Increase Precision (remove noise) |
| **Failure Mode** | Hallucinates if docs are bad | May retrieve too much noise | High latency due to grading step |
| **Key Mechanism** | Single Vector Search | Multi-Query + RRF Ranking | LLM Grader + Web Search fallback |
| **Best Use Case** | Well-curated, clean data | Complex, vague user queries | Mission-critical accuracy / Dynamic data |

### Summary: When to use CRAG?
Use **Corrective RAG** when the cost of a hallucination is high. If your application provides medical, legal, or technical advice where "I don't know" or "Let me search the web" is better than a confident but wrong answer, CRAG is the best choice.

## References
- [Corrective RAG](https://emergent.sh/glossary/corrective-rag)
- [What is Corrective RAG?](https://www.youtube.com/watch?v=gPjewYUKuEo&t=16s)
- [Corrective RAG (CRAG): Workflow, implementation, and more](https://www.meilisearch.com/blog/corrective-rag)
- [Tavily: LangChain documentation](https://js.langchain.com/v0.1/docs/integrations/retrievers/tavily/)
