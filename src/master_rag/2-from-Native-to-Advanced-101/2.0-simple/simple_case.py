import os
# Define o User Agent antes de qualquer import do LangChain para remover o aviso do console
os.environ["USER_AGENT"] = "master-rag-app"
import warnings

from dotenv import load_dotenv
from colorama import Fore

# LangChain Imports
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# Instead FAISS
from langchain_core.vectorstores import InMemoryVectorStore


warnings.filterwarnings("ignore", category=DeprecationWarning)

# LOAD ENV VARIABLES
load_dotenv()

def format_docs(docs):
    print("Retrived documents:", len(docs))
    return "\n\n".join([d.page_content for d in docs])

# Setup Model and Embeddings
llm = ChatOpenAI(model="qwen2.5:7b", base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# Indexing: Load Documents and Create thd DB Vector Store (Done once at startup)
loader = WebBaseLoader("https://www.ibm.com/br-pt/think/topics/llamaindex-vs-langchain")
documents = loader.load()
db = InMemoryVectorStore.from_documents(documents, embeddings)

# Set the retriever over the Vector DB
retriever = db.as_retriever(search_kwargs={"k": 1})

prompt = ChatPromptTemplate.from_template("""
You are a senior developer who answer the question based only on the following context:
{context}

Question: {question}
""")

retrieval_chain = (
    {
        "context": RunnablePassthrough() | retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


def ask():
    while True:
        user_input = input("Q: ")
        if user_input.lower() == "x":
            break # Use break to return to the start menu
        else:
            response = retrieval_chain.invoke(user_input)
            print(Fore.BLUE + f"A: " + response + Fore.RESET)
            print(Fore.WHITE + "\n-------------------------------------------------")

def start():
    instructions = (
        "Type your question and press ENTER. Type 'x' to go back to the MAIN menu.\n"
    )
    print(Fore.BLUE + "\n\x1B[3m" + instructions + "\x1B[0m" + Fore.RESET)

    print("MENU")
    print("====")
    print("[1]- Ask a question")
    print("[2]- Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        ask()
        start() # Return to menu after finishing asking
    elif choice == "2":
        print("Goodbye!")
        exit()
    else:
        print("Invalid choice")
        start()

if __name__ == "__main__":
    start()
