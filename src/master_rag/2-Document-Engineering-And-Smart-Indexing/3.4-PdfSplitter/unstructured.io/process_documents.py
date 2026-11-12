import os

from colorama import Fore
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from unstructured.documents.elements import CompositeElement, Table
from unstructured.partition.pdf import partition_pdf
from utils import load_img_to_image_str

load_dotenv()

filepaths = ["./docs/text-splitters.pdf", "./docs/rag.pdf"]
pdf_elements = []
documents = []
UNSTRUCTURED_API_KEY = os.environ.get("UNSTRUCTURED_API_KEY")

LANGUAGE_MODEL = "gemma3:4b" #   "qwen2.5vl:7b"  # "minicpm-v"   # "llava"

# -------------------------- LLM and Embedding Models --------------------------
llm = ChatOpenAI(model=LANGUAGE_MODEL, base_url="http://localhost:11434/v1", temperature=0)

#init client

def element_to_document(element):
    if isinstance(element, CompositeElement):
        content = element.text  # Assuming CompositeElement has a text attribute
    elif isinstance(element, Table):
        content = str(element.to_dict())  # Assuming Table has a to_list method to convert to a list
    else:
        content = str(element)  # Fallback to string representation for unknown types
    return Document(page_content=content)


# Extracts the elements from the PDF
def extract_elements_from_pdf(filepaths):
    """ extract elements from pdf with partition_pdf"""
    for filepath in filepaths:
        pdf_elements = partition_pdf(
            filename=filepath,
            strategy="hi_res", 
            model="yolox",
            infer_table_structure=True,
            extract_images_in_pdf=True, 
        )

    documents.append(pdf_elements)


def describe_images_from_pdf():
    """Describe images from PDFs."""
    images = load_img_to_image_str()
    if not images:
        print("No images!")
        return False

    for base64_image in images:
        msg = llm.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Please give a short description of the image provided."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                )
            ]
        )
        print(Fore.GREEN + f"Image description: {msg.content}")
        documents.append(Document(page_content=msg.content))
        
        

def process_pdf_documents():
    """Process the PDF documents and extract elements."""
    print("Processing PDF documents...")  
    extract_elements_from_pdf(filepaths)

    print("Extracting images from PDFs:")
    load_img_to_image_str()

    print("Describing images from PDFs:")
    describe_images_from_pdf()


    flattened_elements_list = [element for sublist in documents for element in sublist]
    docs = [element_to_document(element) for element in flattened_elements_list]
    _ = [print(doc.page_content) for doc in docs]
    print(f"number PDF documents processed. {len(docs)}")
    return docs



