# Project : Text splitters with LangChain 
## Character Text Splitter
The `CharacterTextSplitter` is the most basic text splitter available in LangChain. It splits text based on a **single, user-defined character** (by default, it is `"\n\n"`).

### 1. How it Works
Unlike more advanced splitters, the `CharacterTextSplitter` is very rigid:
1. It searches for the specific `separator` you provided.
2. It splits the text into pieces at every occurrence of that separator.
3. It then combines those pieces into larger "chunks" until the `chunk_size` is reached.
4. If a single piece (between two separators) is larger than the `chunk_size`, it will still keep that piece intact (meaning you might end up with chunks larger than your defined `chunk_size`).

### 2. Key Parameters
*   **`separator`**: The character where the split should occur. (Default: `"\n\n"`)
*   **`chunk_size`**: The maximum number of characters desired in each chunk.
*   **`chunk_overlap`**: The number of characters to overlap between two consecutive chunks. This is crucial for maintaining context between splits.

### 3. Code Example
```python
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
```
Output:
```text
Chunk 1: Hello world. This is a test.
Chunk 2: This is a new paragraph.
Chunk 3: This is another paragraph.
```
### 4. Pros and Cons
| Pros | Cons |
| :--- | :--- |
| **Predictable:** You know exactly where the break happens. | **Inflexible:** If the separator isn't found, it won't split the text at all. |
| **Fast:** Extremely low computational overhead. | **Size Issues:** It can produce chunks larger than `chunk_size` if the separator is missing. |
| **Good for structured data:** Works well if your data has clear markers (e.g., CSV lines or specific delimiters). | **Context Loss:** Hard splits can cut a sentence in half if not configured carefully. |

---

## Recursive Character Text Splitter

The **`RecursiveCharacterTextSplitter`** is the recommended text splitter for most generic text processing tasks in LangChain. 

While the `CharacterTextSplitter` only looks for one specific character, the **Recursive** version is smarter: it tries to split text using a hierarchy of characters to keep semantically related text (like paragraphs and sentences) together as much as possible.

### 1. How it Works (The Logic)
The "Recursive" part means it doesn't just give up if one separator doesn't work. It uses a list of characters (separators) and tries them in order:
1. **First**, it tries to split by **`"\n\n"`** (Double newlines/Paragraphs).
2. **If the chunks are still too large**, it tries **`"\n"`** (Single newlines/Lines).
3. **If still too large**, it tries **`" "`** (Spaces/Words).
4. **Finally**, it tries **`""`** (Individual characters) as a last resort.

**The Goal:** To keep chunks as close to the `chunk_size` as possible while ensuring that paragraphs stay together, then sentences, then words.

### 2. Key Parameters
*   **`chunk_size`**: The maximum number of characters a chunk should contain.
*   **`chunk_overlap`**: How many characters should overlap between chunks. This is critical in RAG to prevent a "semantic break" where a key piece of information is cut in half across two chunks.
*   **`separators`**: (Optional) A list of characters to split on. If not provided, it uses the defaults: `["\n\n", "\n", " ", ""]`.

### 3. Code Example
```python
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
```
Output:
```text
Chunk 1:
LangChain is a framework for developing applications powered by language models.
--------------------
Chunk 2:
It enables components to be chained together.
--------------------
Chunk 3:
One of the most important parts of RAG is text splitting.
--------------------
Chunk 4:
Splitting ensures that the LLM receives the most relevant context without exceeding its token
--------------------
Chunk 5:
exceeding its token limit.
--------------------
Chunk 6:
Recursive splitting is generally better than character splitting because it respects the structure
--------------------
Chunk 7:
the structure of the text.
--------------------
```
## When to use `CharacterTextSplitter` vs `RecursiveCharacterTextSplitter`?
In 90% of LangChain projects, you should actually use the **`RecursiveCharacterTextSplitter`** instead of the `CharacterTextSplitter`.

*   **Use `CharacterTextSplitter` if:** Your text has a very strict, consistent delimiter (like a specific symbol or a double newline) and you want to split *strictly* on that.
*   **Use `RecursiveCharacterTextSplitter` if:** You want the splitter to try multiple characters (e.g., `"\n\n"`, then `"\n"`, then `" "`, then `""`) to ensure the chunks stay as close to the `chunk_size` as possible without breaking words or sentences.


## Why is this better than `CharacterTextSplitter`?
| Feature | `CharacterTextSplitter` | `RecursiveCharacterTextSplitter` |
| :--- | :--- | :--- |
| **Strategy** | Single character $\rightarrow$ Split | Hierarchy of characters $\rightarrow$ Split |
| **Semantic Integrity** | Poor (might cut a sentence in half) | High (tries to keep paragraphs/sentences together) |
| **Chunk Size Accuracy** | Often creates chunks much larger than `chunk_size` | Very accurate to the `chunk_size` |
| **Flexibility** | Low | High |

## Summary: When to use it?
**Use `RecursiveCharacterTextSplitter` by default for almost every project.** 

It is the "gold standard" for RAG (Retrieval Augmented Generation) because it maximizes the quality of the retrieved context by ensuring that the chunks sent to the LLM are coherent and logically grouped.


## References
- [langchain-text-splitters](https://reference.langchain.com/python/langchain-text-splitters)
- [Text splitter integration](https://docs.langchain.com/oss/python/integrations/splitters)
- [Splitting by character - Text splitter integration guide](https://docs.langchain.com/oss/python/integrations/splitters/character_text_splitter)
- [Splitting recursively - Text splitter integration guide](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)