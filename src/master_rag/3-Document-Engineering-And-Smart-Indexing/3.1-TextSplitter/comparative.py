from langchain_text_splitters import CharacterTextSplitter


# Sample text
text = "Hello world. This is a test. \n\n This is a new paragraph. \n\n This is another paragraph."

# Initialize the splitter
text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=50,
    chunk_overlap=10
)

# Split the text
docs = text_splitter.split_text(text)

for i, chunk in enumerate(docs):
    print(f"Chunk {i+1}: {chunk}")

print("-"*60)
print("\n")
# ----------------------------------------------------
from langchain_text_splitters import RecursiveCharacterTextSplitter


# A long piece of text with paragraphs and sentences
text = """
LangChain is a framework for developing applications powered by language models. 
It enables components to be chained together.

One of the most important parts of RAG is text splitting. 
Splitting ensures that the LLM receives the most relevant context without exceeding its token limit.

Recursive splitting is generally better than character splitting because it respects the structure of the text.
"""

# Initialize the Recursive splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,       # Small size for demonstration
    chunk_overlap=20,      # Keep 20 characters from the previous chunk
    separators=["\n\n", "\n", " ", ""] 
)

# Split the text
chunks = text_splitter.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}:\n{chunk}")
    print("-" * 20)
