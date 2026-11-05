# RAG-Fusion: RRF Multi-query
import os
from dotenv import load_dotenv
from colorama import Fore
import warnings

warnings.filterwarnings("ignore")
USER_AGENT = "master-rag-app"
os.environ["USER_AGENT"] = USER_AGENT
load_dotenv()

from langchain_core.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings


# ------------------------ LLM and Embedding Models ------------------------
LANGUAGE_MODEL = "gemma4:31b-cloud"  # "llama3.2" # 

llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")

# ------------------------ Pre-Process: INDEXING ------------------------
# load documents 
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
COLLECTION_NAME = "rag_fusion_blog"

# Connect to the collection (creates it empty if it doesn't exist)
vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# Delete only if it already contains data
existing = vectorstore._collection.count()
if existing > 0:
    print(f"{Fore.YELLOW}Collection '{COLLECTION_NAME}' has {existing} chunks, deleting...{Fore.RESET}")
    vectorstore.delete_collection()
    # Recreate a fresh, empty collection
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

# Index the splits
vectorstore.add_documents(splits)
print(f"{Fore.CYAN}Indexed {vectorstore._collection.count()} chunks{Fore.RESET}")

# Wraps around a VectorStore to search and fetch relevant document chunks based on semantic similarity.
# It automatically passes the query to an embedding model
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 4}  # Restricts output to the top 4 most relevant chunks
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

# https://gist.github.com/srcecde/eec6c5dda268f9a58473e1c14735c7bb
def reciprocal_rank_fusion(results: list[list], k=60):
    """ 
    Reciprocal Rank Fusion (RRF) takes multiple lists of ranked documents and an optional parameter k 
    used in the RRF formula. 

    RRF is a fusion method, not a true reranker. It doesn’t re-score documents against the query with 
    a model (like a cross-encoder); it only merges the rankings that your multiple queries already produced.

    # What it does correctly:
        * Each document gets a score contribution from every list it appears in, so documents retrieved by 
          several of the generated queries are boosted.
        * Documents ranked high in any list contribute more than those ranked low.
        * k=60 is the standard constant from the original paper. It dampens the impact of top ranks so that one list can’t dominate.
        * It uses only ranks, not raw similarity scores, so it works even when the lists come from queries with different score scales.
    """
    # Initialize a dictionary to hold fused scores for each unique document defined by its source and page content
    fused_scores = {}   # key -> score
    doc_by_key = {}     # key -> Document

    # Iterate through each list of ranked documents
    for docs in results:
        # Dedupe within a single list too, so a repeated chunk
        # can't score twice from the same query
        seen_in_list = set()
        rank = 0        # Iterate through each document in the list, with its rank (position in the list)
        for doc in docs:
            key = (doc.metadata.get("source"), doc.page_content.strip())
            # Deduplicate same chunks from same source
            if key in seen_in_list:
                continue
            seen_in_list.add(key)
            rank += 1

            doc_by_key.setdefault(key, doc)
            fused_scores[key] = fused_scores.get(key, 0) + 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    # Return the reranked results as a list of tuples, each containing the document and its fused score
    return [
        (doc_by_key[key], score)
        for key, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

# ----------------------------- RAG FINAL ANSWER PROMPT -----------------------------
rag_template = """Answer the following question based on this context:
{context}
Question: {question}
"""
rag_prompt = ChatPromptTemplate.from_template(rag_template)

# ----------------------------------- RAG Pipeline ----------------------------------
def query(query):
    """ 
    Generate optimized answer for a given query using its multi-queries re-ranked results 
    Suggested Question: How can we make retrieval robust to variability in user input?
    """     
    # Retrieval Chain
    retrieval_chain_rag_fusion = (
        generate_multi_queries() 
        | retriever.map() 
        | reciprocal_rank_fusion
    )

    ranked = retrieval_chain_rag_fusion.invoke({"question": query})

    top_docs = [doc for doc, score in ranked[:4]]  # keep the best few
    print(f"{Fore.CYAN}{len(ranked)} unique docs, using top {len(top_docs)}{Fore.RESET}")
    # Print RRF scores
    print(f"{Fore.GREEN}RRF ranking:{Fore.RESET}")
    for i, (doc, score) in enumerate(ranked, 1):
        used = "✔" if i <= len(top_docs) else " "
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"  {used} #{i:<2} score={score:.5f} | {preview}...")    
    
    # Final RAG Generation Chain (reuses the already retrieved docs)
    final_rag_chain = rag_prompt | llm | StrOutputParser()

    print("-"*60)
    print("Question: ", query)
    
    return final_rag_chain.invoke({"context": top_docs, "question": query})
