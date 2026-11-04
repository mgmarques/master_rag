from dotenv import load_dotenv
from colorama import Fore

from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
# https://docs.langchain.com/oss/python/integrations/vectorstores/chroma

import warnings
warnings.filterwarnings("ignore")

load_dotenv()

LANGUAGE_MODEL = "llama3.2:1b"

template: str = """/
    You are a customer support specialist /
    question: {question}. You assist users with general inquiries based on {context} /
    and technical issues. /
    """
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question", "context"],
    template="{question}",
)
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

model = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
vect_db: VectorStoreRetriever = None

def format_docs(docs):
    print("Retrieved documents:", len(docs))
    return "\n\n".join([d.page_content for d in docs])


def load_documents()->list[Document]:
    """Load a file from path, split it into chunks, embed each chunk and load it into the vector store."""
    raw_documents = TextLoader("docs/user-manual.txt").load()
    # Document Splitter
    text_splitter = RecursiveCharacterTextSplitter(
    # Set the chunk size to very small. These settings are for illustrative purposes only.
    chunk_size=150,
    # Sets the number of overlapping characters between chunks.
    chunk_overlap=50,
    # Specifies a function to calculate the length of the string.
    length_function=len,
    # Sets whether to use regular expressions as delimiters.
    is_separator_regex=False
    )
    docs = text_splitter.split_documents(raw_documents)
    print("Split documents:", len(docs))
    return docs


def load_embeddings(documents, k=4):
    """Create a vector store from a set of documents."""
    global vect_db

    embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")
    # https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma/from_documents
    db = Chroma.from_documents(
        documents=documents, embedding=embeddings,
        # collection_name="washing_machine_support", persist_directory="chroma_langchain_db",
    )

    # Query by turning into retriever
    # You can also transform the vector store into a retriever for easier usage in your chains.
    vect_db = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )

def generate_response(retriever, query):
    """Generate a response using the retriever and the query."""
    # Create a prompt template using a template from the config module and input variables
    # representing the context and question.
    # create the prompt
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | chat_prompt_template
        | model
        | StrOutputParser()
    )
    return chain.invoke(query)


def init_vector_db():
    """Initialize the vector database."""
    documents = load_documents()
    load_embeddings(documents, 2)

def query_vector_db(query: str):
    """
    Query the vector database.

    `retrieve | format_docs` performs a similarity search based
    on the query and returns only the k closest chunks.
    Then, `query_vector_db` is no longer being called
    """
    if vect_db is None:
        init_vector_db()

    docs = vect_db.invoke(query)
    print("Retrieved documents:", len(docs))
    return docs

def query(query):
    """Query the model and return the response."""
    """Query the model and return the response."""
    if vect_db is None:
        init_vector_db()
    return generate_response(vect_db, query)


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
    elif choice == "2":
        print("Goodbye!")
        exit()
    else:
        print("Invalid choice")
        start()


def ask():
    while True:
        user_input = input("Q: ")
        # Exit
        if user_input == "x":
            start()
        else:

            response = query(user_input)

            print(Fore.BLUE + f"A: " + response + Fore.RESET)
            print(Fore.WHITE + "\n-------------------------------------------------")


if __name__ == "__main__":
    start()
