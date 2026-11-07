# Project : Text splitters with LangChain
## Code splitters with Recursive Character Text Splitter
When splitting code, you cannot use a standard text splitter because cutting a function or a class in half makes the code snippet logically useless for an LLM.

To solve this, LangChain provides a specialized method within the `RecursiveCharacterTextSplitter` called **`.from_language()`**. This allows the splitter to recognize the specific syntax of the programming language you are using.

### 1. How it Works
Instead of using generic separators like `\n\n`, the `from_language` method uses separators specific to that language. 

For example, in **Python**, it looks for:
*   `class` definitions
*   `def` function definitions
*   Indentation levels

In **JavaScript**, it might look for:
*   `function` declarations
*   `if/else` blocks
*   Curly braces `{ }`

This ensures that functions and classes stay together in one chunk as much as possible.

### 2. Code Example (Python)
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

# A sample block of Python code
python_code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

def main():
    calc = Calculator()
    print(calc.add(5, 3))

if __name__ == "__main__":
    main()
"""

# Initialize the splitter specifically for Python
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, 
    chunk_size=50, # Small size to demonstrate splitting
    chunk_overlap=0
)

# Split the code
docs = python_splitter.split_text(python_code)

for i, chunk in enumerate(docs):
    print(f"Chunk {i+1}:\n{chunk}")
    print("-" * 20)
```

### 3. Supported Languages
LangChain supports a wide range of languages via the `Language` enum:
*   `Language.PYTHON`
*   `Language.JS` (JavaScript)
*   `Language.TS` (TypeScript)
*   `Language.JAVA`
*   `Language.CPP` (C++)
*   `Language.GO`
*   `Language.RUBY`
*   `Language.HTML`
*   `Language.PHP`
   
You can inspect or pass different programming languages using the Language enum from langchain_text_splitters.

To view the exact hierarchy of separators LangChain uses for a given language, you can call:
```python
separators = RecursiveCharacterTextSplitter.get_separators_for_language(Language.PYTHON)
print(separators)
```

### 4. Comparison: Generic vs. Code Splitter
| Feature | `RecursiveCharacterTextSplitter` (Generic) | `RecursiveCharacterTextSplitter.from_language` |
| :--- | :--- | :--- |
| **Separators** | `\n\n`, `\n`, ` `, `""` | Language-specific (e.g., `def`, `class`, `{}`) |
| **Logic** | Splits based on whitespace/length | Splits based on logical code blocks |
| **Risk** | May cut a function in half | Keeps functions/classes intact |
| **Best Use Case** | Books, Articles, PDFs | `.py`, `.js`, `.cpp`, `.java` files |

### 5. Pro-Tip for RAG with Code
If you are building a code-base QA system:
1.  **Use `from_language`**: It is mandatory for maintaining the logic of the code.
2.  **Increase `chunk_size`**: Code usually requires more context than a sentence. Set your `chunk_size` large enough to fit an average function (e.g., 1000–2000 characters).
3.  **Overlap**: Use a small `chunk_overlap` (e.g., 100 characters) to ensure that if a function is *still* too long and gets split, the second chunk has some context from the first.

### references
- [Splitting code text splitter integration guide](https://docs.langchain.com/oss/python/integrations/splitters/code_splitter)