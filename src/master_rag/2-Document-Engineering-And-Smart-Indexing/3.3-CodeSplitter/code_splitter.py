# Optimize RAG: Document Transformes & Chunking Strategies
## Split documents by Code throgh Recursive Text Splitter
import os
import warnings

warnings.filterwarnings("ignore")
USER_AGENT = "master-rag-app"

from colorama import Fore
from dotenv import load_dotenv

os.environ["USER_AGENT"] = USER_AGENT

load_dotenv()


from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

# ------------------------ LLM and Embedding Models ------------------------
LANGUAGE_MODEL = "gemma4:31b-cloud"  #  "llama3.2"  #   

llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# ---------------------------------- Pre-Process: INDEXING ----------------------------------
loader = WebBaseLoader(
    "https://docs.langchain.com/oss/python/integrations/splitters/code_splitter"
)
documents = loader.load()

def split_code(code_snippet, program_lang):
    program_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language[program_lang.upper()], chunk_size=50, chunk_overlap=0)
    return program_splitter.create_documents([code_snippet])


# INDEXING - Load embeddings and create a vector store 
db = FAISS.from_documents(documents, embeddings)

# ------------------------------- RETRIEVAL and GENERATION ------------------------------
# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = db.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 1}  
)

# prompt templates
retriever_template = """
Extract code snippet from the web page based on the {programming_language} language and the {context} of the 
documents retrieved. Do not include other languages
"""

retriever_prompt = PromptTemplate(
    template=retriever_template,
    input_variables=["context", "programming_language"])

# RETRIEVE code snippet A from web page
def get_code_snippets(language):
    """ get the code snippet given a language """
    retriever_chain = (
        {"programming_language": RunnablePassthrough(), 
        "context": retriever}
        | retriever_prompt 
        | llm 
        | StrOutputParser()
    )

    code_snippet = retriever_chain.invoke(language)
    print(f"{Fore.BLUE}=== CODE SNIPPET:===\n")
    print(f"{code_snippet}{Fore.RESET}")
    return code_snippet

# -------------------------------- RAG Pipeline ---------------------------------
rag_template = """You are a senior developer who can answer {question} in natural language based on {context} /
generate a detailed answer to explain in bullet points (steps) and return the formatteds /
add any imports statements or any other requirements if necessary 
"""

rag_prompt = PromptTemplate(
    template=rag_template,
    input_variables=["context", "question"])

def generate(query: str, vector_store):
    """ generate the response given a query and language """
    rag_chain = (
        {
        "context": vector_store,
        "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain.invoke(query)


def main(query, program_lang):
    code_snippet = get_code_snippets(program_lang)
    docs = split_code(code_snippet, program_lang)
    vector_store = FAISS.from_documents(docs, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    response = generate(query, retriever)
    print(f"{Fore.GREEN}=== ANSWER:===\n")
    print(f"A: {response}{Fore.RESET}")
    print(Fore.WHITE + "\n-------------------------------------------------")



if __name__ == "__main__":
    # query = "What did the president say about Ketanji Brown Jackson"
    program_lang = "python"
    query = f"How to split code in {program_lang.capitalize()}?"
    main(query, program_lang)