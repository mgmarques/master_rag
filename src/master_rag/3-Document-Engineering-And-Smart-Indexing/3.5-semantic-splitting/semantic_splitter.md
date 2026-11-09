# Semantic Splitting
Splitting text based on semantic similarity (also known as semantic chunking) is achieved by breaking a document into individual sentences, converting those sentences into vector embeddings, and placing a boundary wherever the similarity between consecutive sentences drops below a specific threshold.

Unlike traditional fixed-size text splitters that arbitrarily cut text in the middle of sentences or ideas, this method ensures that each chunk represents a single, cohesive topic. It is highly valuable for building robust Retrieval-Augmented Generation (RAG) pipelines. 

Splitting text based on semantic similarity—often called semantic chunking—replaces arbitrary length or character limits with a process that analyzes meaning. Instead of cutting text at a fixed number of words or tokens, it keeps cohesive ideas together.

## How the Semantic Splitting Process Works
1. Sentence Segmentation: The text is first parsed and broken down into individual sentences (e.g., using regex, NLTK, or Spacy). 
2. Embedding Generation: Each sentence is passed through an AI embedding model (like OpenAI's text-embedding-3-small or a Hugging Face BERT model) to turn text into high-dimensional numerical vectors. 
3. Similarity Calculation: The algorithm measures the distance (usually via cosine similarity) between consecutive sentences or sliding windows of sentences. 
4. Thresholding (Breakpoint Detection): If the similarity score between sentence A and sentence B drops significantly below a chosen threshold, it indicates a topic shift. The algorithm inserts a split at that exact peak of divergence. 

## Popular Approaches
1. Embedding-Similarity-Based Chunking
* How it works: Compares the cosine distance between consecutive sentences or sliding windows of sentences (e.g., comparing groups of 3 to 6 sentences).
* Best for: General-purpose RAG (Retrieval-Augmented Generation) pipelines where you want to balance context coherence and chunk size.
* Libraries to use: Frameworks like LangChain (SemanticChunker), LlamaIndex, or standalone tools like semantic-text-splitter.

2. Hierarchical Clustering
* How it works: Groups sentences into clusters based on vector-space proximity rather than strictly sequential drop-offs, building multi-level parent-child or tree-like relationships.
* Best for: Complex documents that weave back and forth between themes or require multi-hop reasoning (such as legal contracts or academic papers).

3. LLM-Based / Proposition Extraction
* How it works: Uses a Large Language Model or specialized prompt (such as DSPy signatures) to rewrite or extract self-contained "propositions" that preserve full contextual meaning.
* Best for: Maximum precision where retaining dense, standalone facts is more critical than processing speed.

## Implementation Methods
### Method 1: Using LangChain (Fastest Out-of-the-Box)
LangChain provides an experimental text splitter specifically designed for this purpose, called SemanticChunker. You can set it to automatically calculate thresholds based on percentiles, standard deviations, or interquartile ranges. 

> pip install langchain-experimental langchain-openai
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

# Initialize the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize the chunker (you can choose breakpoint_threshold_type="percentile", "standard_deviation", or "interquartile")
text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")

# Split your document
with open("your_document.txt", "r") as f:
    text = f.read()

chunks = text_splitter.create_documents([text])

# Print out your cohesive chunks
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ---")
    print(chunk.page_content)
```

### Method 2: Pure Python Implementation (Maximum Control)
If you do not want to rely on heavy wrapper frameworks, you can calculate the splits manually using scikit-learn and a lightweight embedding model. 

```python
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load a lightweight local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

text = "Your long document text goes here..."

# 2. Split text into sentences
sentences = re.split(r'(?<=[.?!])\s+', text)

# 3. Generate embeddings for each sentence
embeddings = model.encode(sentences)

# 4. Calculate cosine similarity between consecutive sentences
similarities = []
for i in range(len(embeddings) - 1):
    sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
    similarities.append(sim)

# 5. Set a threshold (e.g., if similarity drops below the 20th percentile)
threshold = np.percentile(similarities, 20)

# 6. Group sentences into chunks based on the threshold
chunks = []
current_chunk = [sentences[0]]

for i, sim in enumerate(similarities):
    if sim < threshold:
        # Topic shift detected -> start a new chunk
        chunks.append(" ".join(current_chunk))
        current_chunk = [sentences[i+1]]
    else:
        current_chunk.append(sentences[i+1])

chunks.append(" ".join(current_chunk))
```

### Method 3: Using semantic-text-splitter (High-Performance Rust Backend)
For very large scale systems or production applications where Python loops might become a bottleneck, the semantic-text-splitter package is highly recommended. It uses a highly optimized Rust core underneath and integrates smoothly with Hugging Face tokenizers. 
```python
# pip install semantic-text-splitter tokenizers
from semantic_text_splitter import HuggingFaceTextSplitter
from tokenizers import Tokenizer

# Load a standard BERT or alternative tokenizer to track token counts
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
splitter = HuggingFaceTextSplitter(tokenizer)

# Options: You can specify maximum token boundaries while keeping semantic structures intact
chunks = splitter.chunks(text, chunk_capacity=(200, 500)) 
```

## Trade-offs to Keep in Mind
* Computational Cost: Traditional splitters (like RecursiveCharacterTextSplitter) are practically instant because they only count characters. Semantic chunking requires generating vectors for every sentence in your text, which introduces network latency (if using OpenAI/cohere APIs) or CPU/GPU overhead (if running local models). 
* Tuning Thresholds: A threshold that works beautifully for legal documents might over-fragment a fiction novel. You will likely need to visually audit your data or plot your cosine similarities to find the optimal breakpoint setting for your specific dataset. 
* Context Window (Token Limit) is the only constraint: The only risk with variable chunk sizes is if a SemanticChunker groups too many sentences together and creates a chunk that exceeds the model's maximum context window (input token limit).
  - Most modern embedding models have quite large context windows (e.g., 8,192 tokens for text-embedding-3-small or bge-large-en-v1.5).
  - Because semantic chunkers usually operate on a paragraph or multi-paragraph level, it is highly rare for a single semantic chunk to naturally stretch to 8,000 tokens unless your source document contains massive walls of text without any punctuation or logical breaks.

## References
- [Semantic Chunking](https://superlinked.com/blog/semantic-chunking)
- [RAG with Semantic Text Splitting for PDF Documents](https://medium.com/@srmsiva1613/rag-with-semantic-text-splitting-for-pdf-documents-511dc6f18784)
- [Text Splitters Character vs Semantic Chunking](https://www.youtube.com/watch?v=QGoUCijkkMs)
- [Semantic-Text-Splitter - Create meaningful chunks from documents](https://www.youtube.com/watch?v=W_yGjKLcViA)
- [A guide to understand Semantic Splitting for document chunking in LLM applications](https://www.reddit.com/r/LangChain/comments/1erxo60/a_guide_to_understand_semantic_splitting_for/)
- [semantic-split 0.1.0 PyPi Package](https://pypi.org/project/semantic-split/)
- [5 Levels Of Text Splitting](https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb)