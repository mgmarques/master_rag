# Decomposition-query RAG
import os
USER_AGENT = "master-rag-app"
os.environ["USER_AGENT"] = USER_AGENT

import bs4
from dotenv import load_dotenv
from operator import itemgetter
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from utils import format_qa_pair, format_qa_pairs

from colorama import Fore
import warnings

warnings.filterwarnings("ignore")

load_dotenv()

LANGUAGE_MODEL = "gemma4:31b-cloud"

# -------------------------- LLM and Embedding Models --------------------------
llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# --------------------------- Pre-Process: INDEXING ---------------------------

# load documents (data source: https://blog.langchain.dev/)
loader = WebBaseLoader("https://blog.langchain.dev/deconstructing-rag/")
docs = loader.load()

loader = WebBaseLoader("https://blog.langchain.dev/reflection-agents/")
docs.extend(loader.load())

#  split documents, create vector store and load embeddings
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=300, 
    chunk_overlap=50)
splits = text_splitter.split_documents(docs)

# Create the vector store: Index and load embeddings
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 3}  # Restricts output to the top 3 most relevant chunks
)

# ----------------- Query Decompositon: Many Simple Sub-Queries ---------------------
template = """You are a helpful assistant trained to generates multiple sub-questions 
related to an input question. \n
The goal is to break down the input into a set of sub-problems / sub-questions that 
can be answered in isolation. \n
Generate multiple search queries related to: {question} \n
Output (3 queries):"""
prompt_decomposition = ChatPromptTemplate.from_template(template)

def generate_sub_questions(query):
    """ generate sub questions based on user query"""
    # Chain
    generate_queries_decomposition = (
        prompt_decomposition 
        | llm 
        | StrOutputParser()
        | (lambda x: x.split("\n"))
    ) 

    # Run
    sub_questions = generate_queries_decomposition.invoke({"question": query})
    questions_str = "\n".join(sub_questions)
    print(Fore.MAGENTA + "=====  SUBQUESTIONS: =====" + Fore.RESET)
    print(Fore.WHITE + questions_str + Fore.RESET + "\n")
    return sub_questions 

# --------------------------- RETGERIEVAL and GENERATION -------------------------- 
# ------------------------ ANSWER SUBQUESTIONS RECURSIVELY ------------------------ 
template = """Here is the question you need to answer:
\n --- \n {sub_question} \n --- \n

Here is any available background question + answer pairs:
\n --- \n {q_a_pairs} \n --- \n

Here is additional context relevant to the question: 
\n --- \n {context} \n --- \n

Use the above context and any background question + answer pairs to answer the question: \n {sub_question}
"""
prompt_qa = ChatPromptTemplate.from_template(template)


def generate_qa_pairs(sub_questions):
    """ ask the LLM to generate a pair of question and answer based on the original user query """
    q_a_pairs = ""

    for sub_question in sub_questions:
        # chain
        generate_qa = (
            {
                "context": itemgetter("sub_question") | retriever, 
                "sub_question": itemgetter("sub_question"), 
                "q_a_pairs": itemgetter("q_a_pairs")
            }
            | prompt_qa 
            | llm 
            | StrOutputParser()
        )
        answer = generate_qa.invoke({"sub_question": sub_question, "q_a_pairs": q_a_pairs})
        q_a_pair = format_qa_pair(sub_question, answer)
        q_a_pairs = q_a_pairs + "\n --- \n" + q_a_pair 
    

# ---------------------------- ANSWER INDIVIDUALLY ------------------------------
# RAG prompt = https://smith.langchain.com/hub/rlm/rag-prompt
# prompt_rag = hub.pull("rlm/rag-prompt") Depricated or use it from from langchain_classic import hub
# Instead use this:
template_rag = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.

Question: {question} 
Context: {context} 

Answer:"""

prompt_rag = ChatPromptTemplate.from_template(template_rag)


def retrieve_and_rag(prompt_rag, sub_questions):
    """RAG on each sub-question"""
    rag_results = []
    for sub_question in sub_questions:
        retrieved_docs = retriever.invoke(sub_question)

        answer_chain = (
            prompt_rag
            | llm
            | StrOutputParser()
        )
        answer = answer_chain.invoke({"question": sub_question, "context": retrieved_docs})
        rag_results.append(answer)
    
    return rag_results, sub_questions
    
# SUMMARIZE AND ANSWER 

# --------------------------- RAG FINAL ANSWER PROMPT ---------------------------
template = """Here is a set of Q+A pairs:

{context}

to use these to synthesize an answer to the question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# -------------------------------- RAG Pipeline ---------------------------------
def query(query):
    """ 
    Generate optimized answer for a given query using the improved subqueries.
    Suggested Question: 
        queries = [
        "How is context improving AI systems",
        "What are the two main components involved in Basic Reflection",
        "Explain the steps involved in the Reflexion loop"
        ]
    """
    # Retrieval Chain
    sub_questions = generate_sub_questions(query)
    generate_qa_pairs(sub_questions)
    answers, questions = retrieve_and_rag(prompt_rag, sub_questions)
    context = format_qa_pairs(questions, answers)

    # Final RAG Generation Chain (reuses the already retrieved docs as context)    
    final_rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    print("-"*60)
    print("Question: ", query)

    return final_rag_chain.invoke({"question": f"{query}", "context": context})
    