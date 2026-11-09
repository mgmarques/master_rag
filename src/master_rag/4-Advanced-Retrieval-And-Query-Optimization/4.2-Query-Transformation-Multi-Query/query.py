# Multi-query RAG
import os

USER_AGENT = "master-rag-app"
os.environ["USER_AGENT"] = USER_AGENT

import warnings

from colorama import Fore
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

warnings.filterwarnings("ignore")
load_dotenv()

# ------------------------ LLM and Embedding Models ------------------------
LANGUAGE_MODEL = "gemma4:31b-cloud" # "llama3.2" # 

llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# ------------------------ Pre-Process: INDEXING ------------------------
# load documents (data source: https://blog.langchain.dev/)
loader = WebBaseLoader("https://blog.langchain.dev/deconstructing-rag/")
docs = loader.load()

loader = WebBaseLoader("https://blog.langchain.dev/reflection-agents/")
docs.extend(loader.load())

# Split
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=300, 
    chunk_overlap=50)

# Make splits
splits = text_splitter.split_documents(docs)

# Create the vector store: Index and load embeddings
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 2}  # Restricts output to the top 2 most relevant chunks
)

# ------------------------ Multi Query: Different Perspectives ------------------------
template = """You are a research assistant. Your task is to generate three different versions 
of the given user question to retrieve relevant documents from a vector database. 
By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Answer only qith the four questions (the 3 generated and added the original question). 
Do not add any explanations or comments.
The questions generated are no more complex than the original query.
Provide these alternative questions separated by newlines. Original question: {question}"""
multi_query_prompt = ChatPromptTemplate.from_template(template)

# ---------------------------- RETGERIEVAL and GENERATION ---------------------------- 
def generate_multi_queries():
    """ generate multiple queries given a user input """

    def print_queries(queries: list[str]) -> list[str]:
        """
        A plain function to use in the chain, LangChain wraps it as a runnable automatically. 
        It also returns the cleaned list, so retriever.map() no longer receives blank strings, 
        which would otherwise trigger pointless embedding calls.
        """
        # Drop empty lines the LLM may produce
        queries = [q.strip() for q in queries if q.strip()]
        print(f"{Fore.YELLOW}Generated {len(queries)} queries:{Fore.RESET}")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        return queries

    multi_query_llm = (
        multi_query_prompt
        | llm
        | StrOutputParser()
        | (lambda x: x.split("\n"))
        | print_queries 
    )

    return multi_query_llm

def get_unique_union(documents: list[list]):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))

    # Return
    return [loads(doc) for doc in unique_docs]

# ----------------------------- RAG FINAL ANSWER PROMPT -----------------------------
rag_template = """Answer the following question based on this context:
{context}
Question: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(rag_template)

# ----------------------------------- RAG Pipeline ----------------------------------
def query(query):
    """ 
    Generate optimized answer for a given query using its multi-queries 
    Suggested Question: How can we make retrieval robust to variability in user input?
    """ 

    # Retrieval Chain
    retrieval_chain = generate_multi_queries() | retriever.map() | get_unique_union

    docs = retrieval_chain.invoke({"question": query})
    print(f"{Fore.CYAN}{len(docs)} documents retrieved{Fore.RESET}")

    # Final RAG Generation Chain (reuses the already retrieved docs)
    final_rag_chain = rag_prompt | llm | StrOutputParser()    

    print("-"*60)
    print("Question: ", query)
    
    return final_rag_chain.invoke({"context": docs, "question": query})
