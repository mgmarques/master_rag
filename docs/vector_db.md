# Vectors Stores
Vector stores are designed to handle and store vector embeddings.

The key functionalities of a vector store include loading source data, embedding the data, storing the embeddings, and 
enabling efficient querying to find the most similar items.

Embeddings are numerical representations of data points, such as text, images, or other types of content.
* The smaller the distance between 2 vectors, the higher is the relatedness between the retrieved documents and the user query ;
* Large distances mean that there is no relatedness in semantic and in meaning.

When building **Retrieval-Augmented Generation** (RAG) pipelines or LLM applications, choosing the right tool depends 
heavily on your scale, infrastructure, and prototyping speed. To clarify your options: Chroma and ChromaDB are exactly 
the same thing (Chroma is the open-source product, and chromadb is its official Python library wrapper), while FAISS, 
InMemoryVectorStore, and Chroma serve drastically different purposes in an AI stack.

Here is the direct comparison to help you choose the correct tool for your project.

## Core Comparison Overview
| Feature            | FAISS	                                 | InMemoryVectorStore	               | Chroma / ChromaDB                        |
|--------------------|------------------------------------------|-------------------------------------|------------------------------------------|
| Type               | Core Indexing Library	                 | Ephemeral Utility Class	           | Lightweight Developer Database           |
| Primary Focus      | Maximum raw speed & scale                | Quick testing & tiny datasets	   | Developer-friendly local RAG apps        |
| Persistence	      | Manual file exporting	                 | None (Lost when script terminates)  | Automatic (SQLite file or client/server) |
| Metadata Filtering | No native support (Requires custom code) | Basic or non-existent	           | Fully native and queryable               |
| GPU Acceleration   | Yes (Native C++ backend)	             | No	                               | No                                       |

## Deep Dive: Understanding Each Tool
1. **FAISS** (Facebook AI Similarity Search)

Developed by Meta AI, FAISS is a highly optimized mathematical library written in C++ with Python wrappers. 
It is not a database. 
* How it works: It focuses strictly on nearest-neighbor search algorithms (like HNSW and IVF) to find similarities 
  between dense vectors.
* Pros: Unmatched speed; can process billions of vectors with GPU acceleration.
* Cons: No CRUD management. If you want to add or remove a document, or associate a piece of text with an embedding, 
  you have to build that mapping layer yourself.

2. **InMemoryVectorStore**
This is a generic utility class found in orchestration frameworks like LangChain or LlamaIndex.
* How it works: It stores embeddings directly inside a standard Python dictionary or list in your computer's RAM.
* Pros: Zero setup required. It is perfect for unit tests, isolated script execution, or building a quick proof-of-concept.
* Cons: Completely temporary. The moment your Python application or Jupyter Notebook restarts, all saved data is 
  permanently lost. It does not scale beyond a few dozen or hundred items without slowing down significantly.

3. **Chroma / ChromaDB**
Chroma is a full-featured vector database designed specifically as a developer-centric companion for LLM workloads. 
* How it works: Under the hood, Chroma actually utilizes indexing libraries (like HNSW or FAISS concepts) but wraps 
  them in a fully structured database framework. 
* Pros: Highly "developer-first." It manages your raw text documents, automatically generates or stores your embeddings, 
  saves your data natively to your disk via SQLite, and allows you to filter search results by metadata tags 
  (e.g., where={"author": "John"}). 
* Cons: It runs locally inside your app's memory space, meaning it is not natively designed to handle production-grade, 
  distributed multi-billion vector clusters. 

## Which one should you use?
* Use InMemoryVectorStore if you are writing a quick test file, trying out an API, or doing a 10-line tutorial.
* Use Chroma / ChromaDB if you are building an actual desktop app, a local assistant, or a RAG prototype where you need 
  your documents saved across app restarts and want to filter by metadata. 
* Use FAISS if you have strict latency requirements, are handling millions of embeddings on a single server, or have an 
  expert machine learning team capable of managing data persistence and metadata mappings manually. 

## References:
- [LangChain: Vector Store Integrations](https://docs.langchain.com/oss/python/integrations/vectorstores/index#vector-store-integrations)
- [chroma vs faiss](https://zilliz.com/comparison/chroma-vs-faiss)
- [Vector databases explained faiss vs pinecone](https://nareshit.com/blogs/vector-databases-explained-faiss-vs-pinecone)
- [Milvus vs FAISS vs Qdrant vs Chroma — A Deep Take on Four Vector Databases](https://medium.com/@sepehrnorouzi7/milvus-vs-faiss-vs-qdrant-vs-chroma-a-deep-take-on-four-vector-databases-c2b8c67e9fad)
- [Choosing Between FAISS and Chroma for Vector Search](https://www.linkedin.com/posts/drminervasingh_ai-machinelearning-faiss-activity-7351650417576923140-Osip)
- [faiss: facebook AI similarity search](https://www.datacamp.com/blog/faiss-facebook-ai-similarity-search)
- [FAISS vs ChromaDB - Vector Search Comparison](https://www.youtube.com/watch?v=AUrJerdKMU8)
- [chroma-db vs qdrant](https://airbyte.com/data-engineering-resources/chroma-db-vs-qdrant) 
- [Which is better faiss or chroma](https://www.upgrad.com/blog/which-is-better-faiss-or-chroma/)
- [Retrieval Augmented Generation (RAG) with Deep Agents](https://docs.langchain.com/oss/python/deepagents/rag#chroma)
