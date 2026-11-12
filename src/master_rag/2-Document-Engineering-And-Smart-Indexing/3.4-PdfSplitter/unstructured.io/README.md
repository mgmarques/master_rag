# Project : Document Specific Splitters (PDFs, Tables and Images)


## Unstructured.io**
**Unstructured.io** is essentially an "ETL (Extract, Transform, Load) pipeline for LLMs." 

Most of the world's data is "unstructured"—meaning it's trapped in PDFs, Word docs, PowerPoint presentations, HTML pages, and emails. While Large Language Models (LLMs) are powerful, they cannot "read" a raw PDF file; they need clean, formatted text. 

Unstructured.io provides the tools to ingest these messy files, "partition" them (identifying what is a title, what is a table, and what is a paragraph), and clean them so they can be fed into a Vector Database for **RAG (Retrieval-Augmented Generation)**.

### **Core Capabilities**
*   **Partitioning:** Automatically detects the structure of a document (e.g., separating a header from a footer or a table from a body paragraph).
*   **Cleaning:** Removes unnecessary whitespace, boilerplate text, and formatting junk.
*   **Chunking:** Breaks long documents into smaller, meaningful pieces (chunks) so they fit within an LLM's context window.
*   **Connector Ecosystem:** It can pull data directly from S3, SharePoint, Google Drive, and Slack.

### **The Alternatives**
Depending on your budget and technical needs, alternatives fall into four main categories:

#### **1. The "Framework" Integrated Loaders**
If you are already using an LLM framework, you might not need a separate tool.
*   **LangChain / LlamaIndex:** Both have built-in "Document Loaders." 
    *   *Note:* Many of these frameworks actually use Unstructured.io under the hood, but they provide simpler wrappers for basic tasks.

#### **2. Specialized AI Parsers (High Fidelity)**
These are better if your documents have complex layouts (multi-column academic papers, complex financial tables).
*   **Marker:** A high-speed, high-accuracy tool that converts PDFs to Markdown. It is currently very popular for being faster and often more accurate than general tools.
*   **Nougat (by Meta):** Specifically designed for scientific documents and heavy mathematical formulas.
*   **LayoutLM:** A model-based approach to understanding the visual layout of a page.

#### **3. Cloud Giant Services (Enterprise/Paid)**
If you have a huge budget and need an API that "just works" with high security and OCR (Optical Character Recognition) built-in.
*   **AWS Textract:** Great for forms and tables.
*   **Azure AI Document Intelligence:** Highly powerful for enterprise-grade form processing.
*   **Google Document AI:** Excellent for specific document types (invoices, IDs).

#### **4. The "Old School" / Low-Level Libraries**
These are free and fast, but they don't "understand" layout. They just extract raw text.
*   **Apache Tika:** The "grandfather" of document extraction. It supports almost every file format but provides raw text rather than structured "elements."
*   **PyMuPDF / PDFMiner:** Python libraries for deep control over PDF coordinates. Great for developers who want to write their own parsing logic.

### **Summary Comparison Table**

| Tool | Best For... | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Unstructured.io** | General RAG Pipelines | Versatile, handles many formats | Can be heavy/complex to self-host |
| **Marker** | PDF $\rightarrow$ Markdown | Extremely high quality, fast | Narrower focus (mostly PDFs) |
| **AWS/Azure/Google** | Enterprise Scale | Robust OCR, high reliability | Expensive, vendor lock-in |
| **Apache Tika** | Basic Text Extraction | Supports 1000+ formats, fast | No "structural" awareness |
| **LangChain/LlamaIndex** | Quick Prototyping | Integrated into the LLM flow | Often just a wrapper for other tools |

## References
- [Marker Tutorial: Fast PDF to Markdown Conversion in Python](https://pdftomd.cloud/blog/pdf-to-markdown-marker-tutorial)
- [The Best PDF Parsers in 2026](https://link.sc/blog/best-pdf-parsers-2026)
- [Best AI PDF Parsers in 2026: 9 Tools Ranked for Developers](9https://www.llamaindex.ai/insights/best-ai-pdf-parsers)
- [Best Open-Source PDF-to-Markdown Tools in 2026](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)

## Ollama Vision Models Suggestions
Llama 3.2 Vision is an older model, and these tend to work better and use less memory:
ollama pull qwen2.5vl:7b     # strong at documents/charts
or: ollama pull gemma3:4b / minicpm-v / llava

## install tesseract and poppler

Run this in your terminal:

```bash
brew install tesseract poppler
```

- `tesseract` is the OCR engine (the one your error is about).
- `poppler` is needed by `pdf2image` / `unstructured` to convert PDFs to images. You'll hit that error next if you skip it.

For Portuguese documents (since you're in Brazil), also add the language data:

```bash
brew install tesseract-lang
```

That installs all languages. It's large, so if you only want Portuguese, you can instead download `por.traineddata` into the tessdata folder (`brew --prefix tesseract` shows where Tesseract lives; the folder is `share/tessdata`).

Then verify:

```bash
tesseract --version
tesseract --list-langs
```

**If Python still can't find it**, it's usually because your IDE or Jupyter was launched before the install, or doesn't inherit the Homebrew PATH (especially on Apple Silicon, where Homebrew lives in `/opt/homebrew/bin`). Fixes:

1. Restart the Jupyter kernel / VS Code / terminal.
2. Check that `which tesseract` prints `/opt/homebrew/bin/tesseract`.
3. As a last resort, set the path explicitly at the top of your script or notebook:
   ```python
   import os
   os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
   ```

Then, when calling `unstructured`, pass the language so OCR uses it:

```python
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf("file.pdf", strategy="hi_res", languages=["por"])
```

Note that `strategy="hi_res"` and `"ocr_only"` use Tesseract, while the default `"auto"` may fall back to it for scanned pages. If your PDFs have selectable text, `strategy="fast"` avoids OCR entirely.