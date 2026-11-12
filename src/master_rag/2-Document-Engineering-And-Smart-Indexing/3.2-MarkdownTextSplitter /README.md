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

---

## Other Types of Text Splitters
1. Word-Based Splitters
* **Whitespace Splitter**: Splits text based on spaces and common whitespace characters (e.g., tabs, newlines).
Example: Splitting "Hello world!\nWelcome." by whitespace results in ["Hello", "world!", "Welcome."].

* **Custom Delimiter Splitter**: Splits text using custom word boundaries or punctuation.
Example: Splitting "Hello-world!" by "-" results in ["Hello", "world!"].

2. Line-Based Splitters
* **Single Line Splitter**: Splits text into individual lines.
Example: Splitting "Hello world!\nWelcome." by lines results in ["Hello world!", "Welcome."].

* **Multi-Line Splitter**: Splits text by multiple lines or paragraph markers.
Example: Splitting "Hello world!\n\nWelcome." by paragraphs results in ["Hello world!", "Welcome."].

3. Sentence-Based Splitters
* **Punctuation-Based Splitter**: Splits text into sentences using punctuation marks (e.g., periods, exclamation marks, question marks).
Example: Splitting "Hello world! How are you?" by sentences results in ["Hello world!", "How are you?"].

* **Advanced Sentence Splitter**: Uses natural language processing (NLP) to accurately split sentences, considering abbreviations and other linguistic nuances.
Example: Splitting "Dr. Smith is here. He said, 'Hello world!'" results in ["Dr. Smith is here.", "He said, 'Hello world!'"].

4. Paragraph-Based Splitters
* **Newline-Based Splitter**: Splits text into paragraphs based on newline characters.
Example: Splitting "Hello world!\n\nWelcome to the text splitter." by paragraphs results in ["Hello world!", "Welcome to the text splitter."].

* **Indentation-Based Splitter**: Uses indentation or specific paragraph markers to split text.
Example: Splitting " Hello world!\n Welcome to the text splitter." by indentation results in [" Hello world!", " Welcome to the text splitter."].

5. Regex-Based Splitters
* **Simple Regex Splitter**: Uses regular expressions to define custom split points.
Example: Splitting "Hello1world2!" by digits (regex \d) results in ["Hello", "world", "!"].

* **Complex Regex Splitter**: Utilizes more advanced regex patterns to handle complex splitting criteria.
Example: Splitting "Hello, world! (Welcome to the text splitter)" by non-word characters (regex \W+) results in ["Hello", "world", "Welcome", "to", "the", "text", "splitter"].

6. Token-Based Splitters
* **Word Tokenizer**: Splits text into tokens, which are usually words, but can include punctuation based on the tokenizer settings.
Example: Splitting "Hello, world!" results in ["Hello", ",", "world", "!"].

* **Subword Tokenizer**: Splits text into smaller units, such as subwords or syllables.
Example: Splitting "unhappiness" into ["un", "happiness"].

## References
- [langchain-text-splitters](https://reference.langchain.com/python/langchain-text-splitters)
- [Split markdown - text splitter integration](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
- [Split HTML - text splitter integration](https://docs.langchain.com/oss/python/integrations/splitters/split_html)