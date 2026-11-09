# Optimize RAG: Document Transformes & Chunking Strategies
## Split documents by Reursive Character Text Spltter
import os
import warnings

warnings.filterwarnings("ignore")
USER_AGENT = "master-rag-app"

from colorama import Fore
from dotenv import load_dotenv

os.environ["USER_AGENT"] = USER_AGENT

load_dotenv()

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ------------------------ LLM and Embedding Models ------------------------
LANGUAGE_MODEL = "llama3.2"  # "gemma4:31b-cloud" #  

llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

template: str = "You are a helpful assistant who answers {question} based on {context}"

system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question", "context"],
    template="{question}",
)
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

# ---------------------------------- Pre-Process: INDEXING ----------------------------------
chunk_size = 300

state_of_the_union = TextLoader("../data/state_of_the_union.txt").load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=0
)

def load_documents():
    return text_splitter.split_documents(state_of_the_union)


documents = load_documents()
vector_store = Chroma.from_documents(documents, embeddings)

def print_chunks():
    _ = [print(f"{index + 1}/{len(documents)} - {document.page_content}\n") for index, document in enumerate(documents)]

    print(f"{Fore.GREEN}- Chunk Size: {chunk_size}")
    print(f"- Number of chunks: {len(documents)}")

# ------------------------------- RETRIEVAL and GENERATION ------------------------------
# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = vector_store.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 2}  # Restricts output to the top 2 most relevant chunks
)


# -------------------------------- RAG Pipeline ---------------------------------
def main(query):
    """Query the model with a question and assess the relevance of retrieved documents."""    
    print_chunks()
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | chat_prompt_template
        | llm
        | StrOutputParser()
    )
    response = chain.invoke(query)
    print(f"{Fore.CYAN}{response}")


if __name__ == "__main__":
    query = "What did the president say about Ketanji Brown Jackson"
    # query = "What happened to Heath"
    main(query)
