# Decomposition: Query Translation and Enhancement on a RAG LangChain
In the context of LangChain and RAG (Retrieval-Augmented Generation), **Query Translation and Enhancement** refers to 
the process of transforming a raw user query into a more effective version (or multiple versions) before it hits the vector database.

The core problem is that **users are bad at writing queries** that align with how vector embeddings work. They might be 
too vague, too complex, or use terms that don't perfectly match the documents.

Here is a detailed breakdown of the decomposition strategies for Query Translation and Enhancement in LangChain.

### 1. Multi-Query Retrieval (Query Expansion)
Instead of relying on a single query, this technique uses an LLM to generate multiple variations of the same question 
from different perspectives.

*   **How it works:** The LLM takes the user input and generates 3–5 similar questions. Each is used to retrieve documents. The results are then combined (often using Reciprocal Rank Fusion).
*   **Why it helps:** It overcomes the limitation of distance-based similarity search. If the user's phrasing is slightly off, one of the generated variations will likely hit the target.
*   **LangChain Implementation:** Use the `MultiQueryRetriever`.

### 2. Query Decomposition (Sub-Query Generation)
Query decomposition is a strategy to improve question-answering using the power of LLM by re-writing and rephrasing the 
user input to improve retrieval process by **breaking down a question into well-written sub-questions**.

Complex questions often contain multiple implicit questions. 
For example: *"How does the revenue of Company A compare to Company B in 2023?"* 

A vector search for that entire sentence might fail. Decomposition breaks it down.

*   **How it works:**
    1.  **Decompose:** The LLM breaks the complex query into sub-queries:
        *   *Query 1: "What was Company A's revenue in 2023?"*
        *   *Query 2: "What was Company B's revenue in 2023?"*
    2.  **Execute:** Each sub-query is run against the retriever.
    3.  **Synthesize:** The LLM takes the answers to both sub-queries to formulate the final comparison.
*   **Why it helps:** It prevents the "dilution" of the search vector and ensures all parts of a multi-part question are answered.

### 3. Step-Back Prompting (Abstraction)
Step-back prompting involves creating a more generic, high-level version of the query to retrieve broader context.

*   **How it works:**
    *   **Original Query:** *"Why did the specific alloy in the X-15 engine fail during the 1962 test?"*
    *   **Step-Back Query:** *"What are the general principles of alloy failure in high-temperature rocket engines?"*
*   **Process:** The system retrieves documents for both the specific and the abstract query. The broad context helps the LLM reason better about the specific answer.
*   **Why it helps:** It provides the "first principles" or foundational knowledge necessary to answer a highly specific technical question.

### 4. HyDE (Hypothetical Document Embeddings)
HyDE flips the retrieval process on its head. Instead of searching for a question, it searches for an answer.

*   **How it works:**
    1.  **Generate:** The LLM creates a "fake" (hypothetical) answer to the user's question.
    2.  **Embed:** This hypothetical answer is converted into a vector.
    3.  **Retrieve:** The system searches the database for real documents that look like the hypothetical answer.
*   **Why it helps:** A hypothetical answer looks more like a document in the vector store than a question does. This significantly improves the "hit rate" for semantic search.

### Summary Table: Which one to use?
| Technique | Best Used When... | Core Logic |
| :--- | :--- | :--- |
| **Multi-Query** | User queries are vague or phrased poorly. | $\text{1 Query} \rightarrow \text{Many Variations}$ |
| **Decomposition** | Queries are complex or multi-part. | $\text{1 Complex Query} \rightarrow \text{Many Simple Queries}$ |
| **Step-Back** | Queries require deep domain/theoretical knowledge. | $\text{Specific Query} \rightarrow \text{Abstract Concept}$ |
| **HyDE** | There is a "gap" between how users ask and how docs are written. | $\text{Question} \rightarrow \text{Fake Answer} \rightarrow \text{Real Doc}$ |

### How to build this in LangChain (The Workflow)
To implement these, you typically use **LCEL (LangChain Expression Language)**. The flow looks like this:
1.  **Input:** User Query.
2.  **Transformation Chain:** 
    *   `PromptTemplate` $\rightarrow$ `LLM` $\rightarrow$ `OutputParser` (to get a list of strings/queries).
3.  **Retrieval Loop:** 
    *   Pass the list of queries to the `Retriever`.
    *   Use a `set()` or `Unique` filter to remove duplicate documents.
4.  **Generation:** 
    *   Pass the consolidated documents + original query to the final `LLM` for the response.