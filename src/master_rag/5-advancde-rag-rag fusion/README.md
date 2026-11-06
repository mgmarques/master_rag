# Project : Advanced RAG - RAG-Fusion
**RAG-Fusion** is an advanced retrieval technique designed to solve a common problem in standard RAG: **the "poorly phrased query" problem.**

In standard RAG, if a user asks a question in a way that doesn't perfectly align with the vector embeddings of your documents, the retriever will miss the most relevant information. RAG-Fusion fixes this by generating multiple versions of the user's query and fusing the results together.

### The RAG-Fusion Workflow
RAG-Fusion follows a four-step process:

#### 1. Query Generation (Expansion)
Instead of using the user's raw query, you send it to an LLM and ask it to generate **3 to 5 variations** of the question from different perspectives.
*   **User Query:** "How do I improve my LLM's accuracy?"
*   **Generated Variants:**
    1. "What are the best techniques for optimizing LLM performance?"
    2. "How to reduce hallucinations in Large Language Models?"
    3. "Strategies for improving retrieval quality in RAG pipelines?"
    4. "How to fine-tune an LLM for better accuracy?"

#### 2. Multi-Query Retrieval
The system runs a vector search for **every single one** of these queries. This gives you multiple lists of documents. Because the queries are phrased differently, they will likely "hit" different parts of the vector space, capturing documents that the original query would have missed.

#### 3. Reciprocal Rank Fusion (RRF)
Now you have 4 or 5 different lists of documents. Some documents will appear in all lists; some only in one. RRF is the mathematical algorithm used to re-rank these documents to find the most "consistently" relevant ones.

**The RRF Formula:**
$$\text{Score}(d) = \sum_{q \in \text{queries}} \frac{1}{k + \text{rank}(q, d)}$$
*   $k$ is a constant (usually 60) to prevent documents ranked very highly from dominating the score too much.
*   $\text{rank}(q, d)$ is the position of document $d$ in the results for query $q$.

**Example:** If a document is ranked #1 in one list and #2 in another, its score is $\frac{1}{60+1} + \frac{1}{60+2}$. A document that is #10 in all lists might actually end up ranking higher than a document that was #1 in only one list but didn't appear in others.

#### 4. Final Generation
The top-N documents from the fused list are passed to the LLM as context to generate the final answer.

### Conceptual Implementation (Python/LangChain)
Here is how you would structure a RAG-Fusion pipeline:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Setup
llm = ChatOpenAI(model="gpt-4o")
vector_store = FAISS.from_texts(["..."], OpenAIEmbeddings())
retriever = vector_store.as_retriever()

# 2. Query Generation Prompt
query_gen_prompt = ChatPromptTemplate.from_template(
    "You are an AI language model assistant. Your task is to generate 4 different versions of the given user question to retrieve relevant documents from a vector database. Original question: {question}"
)
query_gen_chain = query_gen_prompt | llm | StrOutputParser()

# 3. The RAG-Fusion Process
def rag_fusion(user_query, answers=5):
    # Step 1: Generate multiple queries
    generated_queries = query_gen_chain.invoke({"question": user_query}).split("\n")
    
    # Step 2: Retrieve docs for all queries
    all_results = []
    for q in generated_queries:
        all_results.append(retriever.invoke(q))
    
    # Step 3: Reciprocal Rank Fusion (RRF)
    doc_scores = {}
    for rank_list in all_results:
        for rank, doc in enumerate(rank_list, start=1):
            if doc.page_content not in doc_scores:
                doc_scores[doc.page_content] = 0
            # RRF formula: 1 / (k + rank)
            doc_scores[doc.page_content] += 1 / (60 + rank)
    
    # Sort docs by the fused score
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top K documents (answers)
    return [doc for doc, score in sorted_docs[:answers]]

# Execution
final_context = rag_fusion("How to improve LLM accuracy?")
```

### Why use RAG-Fusion instead of standard RAG?
| Feature | Standard RAG | RAG-Fusion |
| :--- | :--- | :--- |
| **Query Sensitivity** | High (Small change in wording $\to$ different results) | Low (Robust to phrasing) |
| **Recall** | Moderate | Very High (Finds more relevant docs) |
| **Latency** | Fast (1 search) | Slower (Multiple searches + RRF) |
| **Cost** | Low | Slightly Higher (Extra LLM call for queries) |
| **Best For** | Simple, clear queries | Complex, ambiguous, or technical queries |

## References
- [RAG-Fusion: The Next Frontier of Search Technology](https://github.com/Raudaschl/rag-fusion)
- [RAG-Fusion: Enhanced Retrieval-Augmented Generation](https://aiengineering.academy/RAG/08_RAG_Fusion/)
- [RAG From Scratch - RAG Fusion](https://www.youtube.com/watch?v=77qELPbNgxA&t=4s)
- [RAG From Scratch: Query Transformations](https://github.com/langchain-ai/rag-from-scratch/blob/main/rag_from_scratch_5_to_9.ipynb)