import warnings

warnings.filterwarnings("ignore")
USER_AGENT = "master-rag-app"

from colorama import Fore
from dotenv import load_dotenv
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
from process_documents import process_pdf_documents

load_dotenv()

template: str = """/
    You are a senior developer /
    who can answer question {question}based on {context} /
    """
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question", "context"],
    template="{question}",
)
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

LANGUAGE_MODEL = "llama3.2"  #   "gemma4:31b-cloud"

# -------------------------- LLM and Embedding Models --------------------------
model = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest", base_url="http://localhost:11434")


def load_embeddings():
    """Create a vector store from a set of documents."""
    # process documents
    documents = process_pdf_documents()
    db = Chroma.from_documents(documents, embeddings)
    return db.as_retriever()


retriever = load_embeddings()

def generate_response(query):
    """Generate a response to a user query."""

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | chat_prompt_template
        | model
        | StrOutputParser()
    )
    return chain.invoke(query)


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

            response = generate_response(user_input)
            print(f"{Fore.GREEN}==== ANSWER ====")
            print(response + Fore.RESET)
            print(Fore.WHITE + "\n-------------------------------------------------")


if __name__ == "__main__":
    start()
