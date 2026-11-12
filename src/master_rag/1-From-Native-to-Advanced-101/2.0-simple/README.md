# Project : Retrieval Q&A (Memory vector store)
> A basic RAG (Retrieval-Augmented Generation) example with relevant data retrieval from a Vector Store built on top of InMemoryVectorStore and fed by an indexed internet data source, to augment context and answer queries. 

## Simple Retrieval Flow witout spliter:
```text
 +----------+   +-----------+   +--------+   +-----------+   +--------------+
 | Document |--→| Embedding |--→| Vector |--→| Retrieves |--→| Generation   |
 | Loaders  |   | Models    |   | Store  |   | (Augment) |   | (LLM Models) |
 +----------+   +-----------+   +--------+   +-----------+   +--------------+
```

## InMemoryVectorStore
This is a generic utility class found in orchestration frameworks like LangChain or LlamaIndex.
* How it works: It stores embeddings directly inside a standard Python dictionary or list in your computer's RAM.
* Pros: Zero setup required. It is perfect for unit tests, isolated script execution, or building a quick proof-of-concept.
* Cons: Completely temporary. The moment your Python application or Jupyter Notebook restarts, all saved data is 
  permanently lost. It does not scale beyond a few dozen or hundred items without slowing down significantly.

> Use InMemoryVectorStore if you are writing a quick test file,trying out an API, or doing a 10-line tutorial. 

## Main Libraries:
- **[OpenAI](https://python.langchain.com/docs/integrations/platforms/openai)**: is a Python library that provides a simple interface to the OpenAI API. It also provides a command-line interface (CLI) for interacting with the API.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: is a Python library that loads environment variables from a .env file. It is used to load the OpenAI API key from the .env file.
- **[colorama](https://pypi.org/project/colorama/)**: is a Python library to produce colored terminal text and outputs
- **[LangChain: InMemoryVectorStore](https://reference.langchain.com/python/langchain-core/vectorstores/in_memory/InMemoryVectorStore)**: In-memory vector store implementation, that uses a dictionary, and computes cosine similarity for search using numpy.

## References
- [LangChain: Vector Store Integrations](https://docs.langchain.com/oss/python/integrations/vectorstores) - A vector stores embedded data and performs similarity search.
