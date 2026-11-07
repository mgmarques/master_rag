# Project : Text splitters with LangChain 
## Markdown Text Splitter
The **`MarkdownTextSplitter`** is a specialized version of the `RecursiveCharacterTextSplitter`. Instead of using generic characters like spaces or newlines, it is specifically designed to recognize and split text based on **Markdown syntax**.

The goal is to keep sections of a Markdown document (like a specific header and its following content) together in one chunk, preserving the logical structure of the document.

### 1. How it Works
The `MarkdownTextSplitter` understands the hierarchy of Markdown. It uses a set of separators that target Markdown headers and formatting. It attempts to split the text in this general order of priority:

1.  **`#`** (H1 - Main Title)
2.  **`##`** (H2 - Major Section)
3.  **`###`** (H3 - Sub-section)
4.  **`####`** (H4) ... and so on.
5.  **`\n\n`** (Paragraphs)
6.  **`\n`** (Line breaks)
7.  **` `** (Words)

By splitting on headers, the splitter ensures that if you have a section called "Installation" and a section called "Usage," they are more likely to stay separate or be captured as distinct, coherent blocks.

### 2. Key Parameters
Because it inherits from the `RecursiveCharacterTextSplitter`, it uses the same main parameters:
*   **`chunk_size`**: Maximum number of characters per chunk.
*   **`chunk_overlap`**: Number of characters to overlap between chunks to maintain context.

### 3. Code Example
```python
from langchain_text_splitters import MarkdownTextSplitter

# Sample Markdown text
markdown_text = """
# Project Overview
This is the main overview of the project. It explains what the tool does.

## Installation
To install the tool, run:
`pip install my-tool`

## Usage
### Basic Usage
Use the tool by running `my-tool start`.

### Advanced Usage
For advanced configuration, edit the `config.yaml` file.

# License
This project is licensed under MIT.
"""

# Initialize the Markdown splitter
splitter = MarkdownTextSplitter(
    chunk_size=100, 
    chunk_overlap=0
)

# Split the text
chunks = splitter.split_text(markdown_text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}:\n{chunk}")
    print("-" * 30)
```
Output:
```text
Chunk 1:
# Project Overview
This is the main overview of the project. It explains what the tool does.
------------------------------
Chunk 2:
## Installation
To install the tool, run:
`pip install my-tool`
------------------------------
Chunk 3:
## Usage
### Basic Usage
Use the tool by running `my-tool start`.
------------------------------
Chunk 4:
### Advanced Usage
For advanced configuration, edit the `config.yaml` file.
------------------------------
Chunk 5:
# License
This project is licensed under MIT.
------------------------------
```

### 4. Comparison: Markdown vs. Recursive

| Feature | `RecursiveCharacterTextSplitter` | `MarkdownTextSplitter` |
| :--- | :--- | :--- |
| **Primary Goal** | General text coherence | Respecting document hierarchy |
| **Split Logic** | $\text{Paragraph} \rightarrow \text{Sentence} \rightarrow \text{Word}$ | $\text{H1} \rightarrow \text{H2} \rightarrow \text{H3} \rightarrow \text{Paragraph}$ |
| **Best Use Case** | Plain text, emails, books, articles | Technical docs, READMEs, Wiki pages |
| **Structure** | Ignores formatting symbols | Uses `#` and `---` as logical boundaries |

### 5. When to use it?
You should use the `MarkdownTextSplitter` whenever your source data is in `.md` format. 

**Why?** 
In a technical document, the header (e.g., `## Troubleshooting`) provides critical context for the text that follows it. If you use a generic splitter, you might split the "Troubleshooting" header into one chunk and the actual solution into another. The `MarkdownTextSplitter` tries to prevent this, making the retrieval step in RAG significantly more accurate.

## References
- [langchain-text-splitters](https://reference.langchain.com/python/langchain-text-splitters)
- [Split markdown - text splitter integration](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
- [Split HTML - text splitter integration](https://docs.langchain.com/oss/python/integrations/splitters/split_html)