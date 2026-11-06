# Corrective RAG (CRAG)
'''
THE STEPS
1. Let’s skip the knowledge refinement phase as a first pass. 
   This can be added back as a node, if desired.
2. If any documents are irrelevant, let’s opt to supplement retrieval with web search.
3. We’ll use Tavily Search for web search.
4. Let’s use query re-writing to optimize the query for web search.
'''
import os
from dotenv import load_dotenv
from colorama import Fore
from pydantic import BaseModel, Field
import warnings

warnings.filterwarnings("ignore")
USER_AGENT = "master-rag-app"
os.environ["USER_AGENT"] = USER_AGENT
load_dotenv()

from langchain_core.documents import Document
from langchain_core.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings

from colorama import Fore
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

# --------------------------------- LLM and Embedding Models --------------------------------
LANGUAGE_MODEL = "qwen2.5:7b"  # "llama3.2" #  "gemma4:31b-cloud"  # "kimi-k3.1-pro:cloud"

llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# ---------------------------------- Pre-Process: INDEXING ----------------------------------
urls = [
    "http://blog.langchain.dev/deconstructing-rag",
    "https://blog.langchain.dev/enhancing-rag-based-applications-accuracy-by-constructing-and-leveraging-knowledge-graphs/",
    "https://blog.langchain.dev/graph-based-metadata-filtering-for-improving-vector-search-in-rag-applications/",
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Split
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)

# Make Splits
splits = text_splitter.split_documents(docs_list)

# Create the vector store: Index and load embeddings
COLLECTION_NAME = "rag-chroma"

# Connect to the collection (creates it empty if it doesn't exist)
vectorstore = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings)

# Delete only if it already contains data
existing = vectorstore._collection.count()
if existing > 0:
    print(f"{Fore.YELLOW}Collection '{COLLECTION_NAME}' has {existing} chunks, deleting...{Fore.RESET}")
    vectorstore.delete_collection()
    # Recreate a fresh, empty collection
    vectorstore = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings)


# Index the splits
vectorstore.add_documents(splits)
print(f"{Fore.CYAN}Indexed {vectorstore._collection.count()} chunks{Fore.RESET}")

# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 4}  # Restricts output to the top 4 most relevant chunks
)

# ----------------------- Question Re-writer - Knowledge Refinement -----------------------
prompt_template = """
Given a user input {question}, re-write or rephrase the question to optimize the query for 
the model
"""

system_prompt = SystemMessagePromptTemplate.from_template(prompt_template)
human_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question"],
    template="{question}",
)
re_write_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

def rewrite_query(query):
    question_rewriter = re_write_prompt | llm | StrOutputParser()
    new_query = question_rewriter.invoke({"question": query})
    print(f"{Fore.YELLOW}New query: {new_query}{Fore.RESET}")  
    return new_query

# ------------------------------- RETRIEVAL and GENERATION ------------------------------
# ------------------------ Retrieval Grader: Retrieval Evaluator ------------------------
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

    def get_score(self) -> str:
        """Return the binary score as a string."""
        return self.binary_score


def get_score(self) -> str:
    """Return the binary score as a string."""
    return self.binary_score

# ------------------------ LLM with function call ------------------------
structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Evaluetor/Grade Prompt 
system_template = """
You are an evaluator determining the relevance of a retrieved {documents} to a user's query {question}. 
If the document contains keyword(s) or semantic meaning related to the question, mark it as relevant. 
Assign a binary score of 'yes' or 'no' to indicate the document's relevance to the question.
"""

system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["documents", "question"],
    template="{question}",
)
grader_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

def assess_retrieve_docs(query):
    retrieval_grader = grader_prompt | structured_llm_grader | get_score
    docs = retriever.invoke(query)
    doc_txt = docs[0].page_content
    binary_score = retrieval_grader.invoke({"question": query, "documents": doc_txt})
    return binary_score, docs

### Web Search Tool - Knowledge Searching ####
web_search_tool = TavilySearchResults(k=3) 

def search_web(query):
    docs = web_search_tool.invoke({"query": query})
    web_results = "\n".join([doc["content"] for doc in docs])
    return Document(page_content=web_results)

# --------------------------- RAG FINAL ANSWER PROMPT ---------------------------
rag_template = """Answer the following question based on this context:
{context}
Question: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(rag_template)

# -------------------------------- Final RAG Step ---------------------------------
def generate_answer(docs, query):
    # Chain
    rag_chain = rag_prompt | llm | StrOutputParser()

    # Run
    return rag_chain.invoke({"context": docs, "question": query})

# -------------------------------- RAG Pipeline ---------------------------------
def query(query):
    """
    Query the model with a question and assess the relevance of retrieved documents.

    Suggested Question: 
     * Relevant: Can you tell me some RAG advanced techniques and their applications?  
     * Irrelevant: What is the temperature in grous celcios now at Porto Alegre?

    """
    # Rewrite the query
    print(f"{Fore.YELLOW}Rewriting and optmize the query...{Fore.RESET}")  
    optimized_query = rewrite_query(query)
    # Evaluate
    binary_score, docs = assess_retrieve_docs(optimized_query)
    print("Relevance Score:", binary_score)
    #  if they are of low quality triggers external knowledge searches to correct or supplement irrelevant or insufficient information.
    if binary_score == "no":
        print(f"{Fore.MAGENTA}Retrieval is not relevant. Searching the web...{Fore.RESET}")
        docs = search_web(optimized_query) 
    return generate_answer(docs, optimized_query)