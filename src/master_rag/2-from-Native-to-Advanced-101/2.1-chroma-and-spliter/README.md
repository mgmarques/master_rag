# Project : Q&A RAG (Chroma vector store)
> A more complete example of RAG (Retrieval Augmented Generation) with relevant data snippets retrieved from a Vector Repository built on Chroma, indexed and loaded with split text from the internet data source, to augment context and answer queries.

## Typical Retrieval Flow:
```text
 +----------+   +---------+   +-----------+   +--------+   +-----------+   +--------------+
 | Document |--→| Text    |--→| Embedding |--→| Vector |--→| Retrieves |--→| Generation   |
 | Loaders  |   | Spliter |   | Models    |   | Store  |   | (Augment) |   | (LLM Models) |
 +----------+   +---------+   +-----------+   +--------+   +-----------+   +--------------+
```

## Chroma / ChromaDB
Chroma is a full-featured vector database designed specifically as a developer-centric companion for LLM workloads. 
* Hierarchy: Tenant -> Database -> Collection -> Document
* How it works: Under the hood, Chroma actually utilizes indexing libraries (like HNSW or FAISS concepts) but wraps 
  them in a fully structured database framework. 
* Pros: Highly "developer-first." It manages your raw text documents, automatically generates or stores your embeddings, 
  saves your data natively to your disk via SQLite, and allows you to filter search results by metadata tags 
  (e.g., where={"author": "John"}). 
* Cons: It runs locally inside your app's memory space, meaning it is not natively designed to handle production-grade, 
  distributed multi-billion vector clusters. 

> Use Chroma / ChromaDB if you are building an actual desktop app, a local assistant, or a RAG prototype where you need your documents saved across app restarts and want to filter by metadata. 

## Main Libraries:
- **OpenAI**: [OpenAI](https://python.langchain.com/docs/integrations/platforms/openai) - is a Python library that provides a simple interface to the OpenAI API. It also provides a command-line interface (CLI) for interacting with the API.
- **python-dotenv**: [python-dotenv](https://pypi.org/project/python-dotenv/) - is a Python library that loads environment variables from a .env file. It is used to load the OpenAI API key from the .env file.
- **colorama**: [python-dotenv](https://pypi.org/project/colorama/) - is a Python library to produce colored terminal text and outputs
- **ChromaDB** : [chromaDB](https://python.langchain.com/v0.2/docs/integrations/vectorstores/chroma/) : Chroma is a AI-native open-source vector database focused on developer productivity

## References
- [Chroma integration with LangChais](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma)
- [Introduction to ChromaDB](https://www.geeksforgeeks.org/nlp/introduction-to-chromadb/)
- [Chroma DB Tutorial: A Step-By-Step Guide](https://www.datacamp.com/tutorial/chromadb-tutorial-step-by-step-guide)