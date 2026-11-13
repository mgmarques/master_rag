# The Ultimate RAG Mastery Blueprint: From Native to Agentic
This blueprint is divided into six progressive phases, moving from a basic "Chat with PDF" setup to a stateful, multi-agent system capable of processing multimodal data.

## Phase 1: LangChain Abstract Layers Foundations
Before building RAG, you must master the interface between the application and the model.
*   **Core LLM Capabilities:** Understanding tokens, context windows, temperature, and the difference between Base models and Instruct-tuned models.
*   **LangChain Core**: Starting the Python Notebooks series to understand the 4 levels of abstraction and the basic elements, let's look at the building blocks of the LangChain core through examples,
*   **LangGraph Orchestration**: Let's built graphs by hand: state with a reducer, nodes, edges, a conditional edge, a tool loop, a second LLM node, observability, memory in two flavors, and a way to inspect and replay the whole thing.
*   **LangChain Agent**: Let's go through it with a code example to build an agent in a single line, seeing that it is really a LangGraph graph, given its tools, memory, and structured output, shaped with middleware, and let it drive a real browser through an MCP server.
*   **LangChain Deep Agents:** Let's introduce the topic by creating a Deep Agent that planned its own work, searched the web, wrote files to disk, delegated to a sub-agent, and turned its findings into a branded PowerPoint slide by following an Agent Skill.
*   **Complete AI Agent**: We are going to build the Sidekick; with it, you will have traversed the entire technology stack: the fundamental components of Layer 1, LangGraph orchestration, the creation of agents (create_agent) at Layer 3, the structure of Deep Agents, and—now—a real-world project that combines all these elements, including middleware for planning, guardrails, and human-in-the-loop approval. It is a robust set of features, and you understand each of its layers. 
*   **The "Native" RAG Pipeline (RAG 101):** 
    *   Implementing the basic flow: **Load $\rightarrow$ Split $\rightarrow$ Embed $\rightarrow$ Store $\rightarrow$ Retrieve $\rightarrow$ Generate**.
    *   **Hands-on:** Building a basic Q&A system using **InMemoryVectorStore** or **ChromaDB** for local vector storage.

## Phase 2: Document Engineering & Smart Indexing
The quality of your RAG is capped by the quality of your data. "Garbage in, garbage out."
*   **Document Transformers:** Using tools to clean and normalize text before it is embedded.
*   **Advanced Chunking Strategies:** Moving beyond fixed-size chunks.
    *   **Character Splitting:** Basic fixed-size blocks.
    *   **Recursive Character Splitting:** Splitting by paragraphs, then sentences, to preserve structural meaning.
    *   **Semantic Chunking:** Using embeddings to find "breakpoints" in text where the meaning changes, ensuring each chunk is a coherent concept.
*   **Scaling Embeddings:** Strategies for handling massive datasets, including batch processing and choosing the right embedding dimension.

## Phase 3: Advanced Retrieval & Query Optimization
Redundancy, incosistencies, and overlap of retieved documents. This is where you solve the "poorly phrased query" and "irrelevant result" problems. 
*   **Pre-Retrieval Optimization by Query Transformation:** Rewriting user queries for better vector matching. 
    *   **Step-back prompting:** Involves creating a more generic, high-level version of the query to retrieve broader context.
    *   **Query Decomposition:** Using the power of LLMs by rewriting and rephrasing the user input to improve the retrieval process by breaking down a question into well-written sub-questions.
    *   **Multi-Query Retrieval/(Query Expansion)**: Generating multiple query variations to increase recall.
    *   **Hypothetical Document Embeddings:** HyDE flips the retrieval process on its head. Instead of searching for a question, it searches for an answer.
*   **Retrieval Optimization:** 
    * **Hybrid Search:** Combining Vector search for semantics and BM25 for keyword precision.
    * **Fine Tuning Embedding Model:** Fine-tuning a pre-trained model helps the model to understand the nuances of a specific domain or dataset, and as a consequence, you can significantly improve the relevance and accuracy of retrieved documents.
*   **Post-Retrieval Optimization:**
    *   **RAG-Fusion:** Builds on the multi-query approach by re-ranking the returned documents from each sub-question for better RAG accuracy and relevance.
    *   **RRF (Reciprocal Rank Fusion):** Merges the rankings that your multiple queries already produced, by an optional parameter k.
    *   **Re-Ranking:** Using Cross-Encoders (like Cohere) to precisely score the top 5 documents.
    *   **Context Compression:** Stripping noise from chunks to save LLM tokens.
    *   **Corrective RAG**: CRAG is an enhancement to standard RAG that evaluates the quality of retrieved documents and triggers external knowledge searches to correct or supplement irrelevant or insufficient information.
    *   **Response Summarization**: Summarize using an LLM or a pre-trained BART model. This step may be necessary if you stored large chunks of text vectors in a database during the indexing process. 

## Phase 4: Enhanced Quality & Multimodal RAG
Real-world data is not just clean text; it is trapped in PDFs, tables, and images.
*   **Unstructured Data Processing:** Using libraries (like Unstructured.io or PyMuPDF) to parse complex layouts.
*   **Structured RAG:**
    *   **Table Extraction:** Converting PDF tables into Markdown or JSON so the LLM can reason over rows and columns.
    *   **Visual RAG:** Integrating **GPT-4 Vision** to analyze images, charts, and diagrams embedded in documents.
    *   **Multimodal Indexing:** Storing image descriptions (summaries) in the vector store to make images searchable.

## Phase 5: Multi-Agent Orchestration with LangGraph
Moving from a "Chain" (Linear) to a "Graph" (Cyclical/Agentic).
*   **Stateful Applications:** Using **LangGraph** to maintain a "memory" (state) of the conversation and the retrieval progress.
*   **Collaborative Agents:** Designing a system where different agents have specialized roles:
    *   *The Researcher:* Handles the retrieval and RAG-Fusion.
    *   *The Grader (CRAG):* Evaluates the quality of retrieved documents.
    *   *The Writer:* Synthesizes the final answer.
    *   *The Critic:* Checks for hallucinations and sends the process back to the Researcher if the answer is lacking.
*   **Control Flow:** Implementing conditional edges (If $\rightarrow$ Then) to decide whether to search the web or generate the final response.

## Phase 6: Production Lifecycle (Debug, Test, Monitor)
An LLM app is never "finished"; it is continuously optimized.
*   **Observability with LangSmith:**
    *   **Tracing:** Visualizing every step of the chain to see exactly where a retrieval failed.
    *   **Debugging:** Identifying which prompt variation or chunk size led to a hallucination.
    *   **Dataset Creation:** Turning real-user queries into test sets for regression testing.
*   **Evaluation Frameworks:**
    *   **Faithfulness:** Does the answer come *only* from the retrieved context?
    *   **Answer Relevance:** Does the answer actually address the user's question?
    *   **Context Precision:** Were the retrieved documents actually useful?


### Summary Mapping: Concept $\rightarrow$ Tool $\rightarrow$ Goal
| Need | Implementation Technique | Tool/Framework | Goal |
| :--- | :--- | :--- | :--- |
| **Data Quality** | Semantic Chunking $\rightarrow$ Transformers | LangChain / Unstructured | High-fidelity context |
| **Search Recall** | Query Decomposition $\rightarrow$ RAG-Fusion | LangChain / Hybrid Search | Find the needle in the haystack |
| **Search Precision** | Re-Ranking $\rightarrow$ Grading (CRAG) | Cohere / GPT-4o | Eliminate noise/hallucinations |
| **Complex Data** | PDF Table Extraction $\rightarrow$ Vision | GPT-4 Vision / PyMuPDF | Handle images & tables |
| **Complex Logic** | Multi-Agent State Graphs | LangGraph | Solve multi-step problems |
| **Reliability** | Tracing $\rightarrow$ Eval $\rightarrow$ Monitoring | LangSmith | Production-grade stability |

---

## 🚀 Setup

### Prerequisites
- The [Chrome](https://www.google.com/chrome/) browser is recommended
- [git](https://git-scm.com/install/) is recommended
- A package/project manager: [uv](https://docs.astral.sh/uv/) (recommended) or [pip](https://pypi.org/project/pip/)
- note: `uv` is also required in Module 2, Lesson 1 to run the MCP server with `uvx`
- Requires Python >=3.12, <3.14  If you use `uv`, it will take care of this for you. [More info](#python-virtual-environments)

### Installation
Open a terminal on the root directory of this project.

Make a copy of example.env
```bash
# Create .env file
cp example.env .env
```

Edit the .env file to include the keys below for [Models](#model-providers) and optionally [LangSmith](#getting-started-with-langsmith)

- Get an OpenAI API Key [here](https://openai.com/index/openai-api/).  
- Optional for Module1/Lesson1, get an Anthropic API Key [here](https://console.anthropic.com) and a Google API Key [here](https://ai.google.dev/gemini-api/docs/quickstart).
- Optional, Create a [LangSmith](https://smith.langchain.com/) account and API Key.  

```bash
# Manual installs for checking: uv

# Required
OPENAI_API_KEY='your_openai_api_key_here'
TAVILY_API_KEY='your_tavily_api_key_here'

# optional, only used in Module1, Lesson 1 once
ANTHROPIC_API_KEY='your_anthropic_api_key_here'
GOOGLE_API_KEY='your_google_api_key_here'

# Optional for evaluation and tracing
LANGSMITH_API_KEY='your_langsmith_api_key_here'
# uncomment to set tracing to true when you set up your LangSmith account
#LANGSMITH_TRACING=true
LANGSMITH_AGENT_ID=lca-lc-foundations
LANGSMITH_AGENT_ENVIRONMENT=local
# Uncomment the following if you are on the EU instance:
#LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Make a virtual environment and install dependencies. [More info](#python-virtual-environments)

<details open>
<summary>Using uv (recommended)</summary>

```bash
uv sync
```

</details>

<details>
<summary>Using pip</summary>

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

### Setup Verification

After completing the Setup section, we recommend you run the following command to verify your environment.

<details open>
<summary>Using uv</summary>

```bash
uv run python env_utils.py
```

</details>

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python env_utils.py
```

</details>

[If the script flags issues, see this section below.](#setup-verification-issues)

### Run Notebooks [More Info](#development-environment)

<details open>
<summary>Using uv (recommended)</summary>

```bash
uv run jupyter lab
```

</details>

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
jupyter lab
```

</details>

### Run Studio (optional)

Ensure you are in the notebooks/module-1 or notebooks/module-3 directory

 <details open>
<summary>Using uv (recommended)</summary>

```bash
uv run langgraph dev
```

</details>

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
langgraph dev
```

</details>

## 📖 Related Resources
### Setup Verification Issues
**What the verification procedure checks:**
- ✅ Python executable location and version (must be >=3.12, <3.14)
- ✅ Virtual environment is properly activated
- ✅ Required packages are installed with correct versions
- ✅ Packages are in the correct Python version's site-packages
- ✅ Environment variables (API keys) are properly configured

**Configuration Issues and Solutions:**

<details>
<summary>ImportError when running env_utils.py</summary>

If you see an error like `ModuleNotFoundError: No module named 'dotenv'`, you're likely running Python outside the virtual environment.

**Solution:**
- Use `uv run python env_utils.py` (recommended), or
- Activate the virtual environment first:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`

</details>

<details>
<summary>Environment Variable Conflicts</summary>

If you see a warning about "ENVIRONMENT VARIABLE CONFLICTS DETECTED", you have API keys set in your system environment that differ from your .env file. Since `load_dotenv()` doesn't override existing variables by default, your system values will be used.

**Solutions:**
1. Do nothing and accept the system environment variable value
2. Unset the conflicting system environment variables for this shell session (commands provided in warning)
3. Use `load_dotenv(override=True)` in your notebooks to force .env values to take precedence
4. Update your .env file or shell init so the values are in agreement

</details>

<details>
<summary>LangSmith Tracing Errors</summary>

If you see "LANGSMITH_TRACING is enabled but LANGSMITH_API_KEY still has the example/placeholder value", you need to either:
1. Set a valid LangSmith API key in your .env file, or
2. Comment out or set `LANGSMITH_TRACING=false` in your .env file

Note: LangSmith is optional for evaluation and tracing. 

</details>

<details>
<summary>Wrong Python Version</summary>

If you see a warning about Python version not satisfying requirements, you need Python >=3.12 and <3.14.

**Solution:**
- If using `uv`: Run `uv sync` which will automatically install the correct Python version
- If using pip: Install Python 3.12 or 3.13 using [pyenv](#python-virtual-environments) or from [python.org](https://www.python.org/downloads/)

</details>

### Python Virtual Environments
Managing your Python version is often best done with virtual environments. This allows you to select a Python version for this project independent of the system Python version.

<details open>
<summary>Using uv (recommended)</summary>

`uv` will install a version of Python compatible with the versions specified in the `pyproject.toml` in the `.venv` directory when running the `uv sync` specified above. It will use this version when invoking with `uv run`. For additional information, please see [uv](https://docs.astral.sh/uv/).
</details>

<details>
<summary>Using pyenv + pip</summary>

If you are using pip instead of uv, you may prefer using pyenv to manage your Python versions. For additional information, please see [pyenv](https://github.com/pyenv/pyenv).

```bash
pyenv install 3.12
pyenv local 3.12
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

</details>

### Model Providers
This project has been created using particular models and model providers.  You can use other providers, but you will need to update the API keys in the `.env` file and make some necessary code changes. LangChain supports many chat model providers. [More Info](https://docs.langchain.com/oss/python/integrations/providers/all_providers).

For OpenAI models that require the Responses API, such as `gpt-5.6-luna`, initialize the model explicitly and pass it to `create_agent`:

```python
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

model = init_chat_model(
    "gpt-5.6-luna",
    model_provider="openai",
    use_responses_api=True,
)
agent = create_agent(model=model)
```

Tavily is a search provider that returns search results in an LLM-friendly way. They have a generous free tier. [Tavily](https://tavily.com)

### Getting Started with LangSmith
- Create a [LangSmith](https://smith.langchain.com/) account
- Create a LangSmith API key

<img width="600" alt="LangSmith Dashboard" src="https://github.com/user-attachments/assets/e39b8364-c3e3-4c75-a287-d9d4685caad5" />

<img width="600" alt="LangSmith API Keys" src="https://github.com/user-attachments/assets/2e916b2d-e3b0-4c59-a178-c5818604b8fe" />

- Create an agent in your LangSmith workspace and copy its agent ID into `LANGSMITH_AGENT_ID` in `.env`; `lca-lc-foundations` in the templates is an example ID, not a workspace or project name
- Set `LANGSMITH_AGENT_ENVIRONMENT=local` for notebook runs; the supported environments are `local`, `development`, `staging`, and `production`
- Update `.env` with your LangSmith API key and uncomment `LANGSMITH_TRACING=true` only after configuring the agent and environment
- Remove legacy `LANGSMITH_PROJECT` and `LANGCHAIN_PROJECT` settings from `.env` and your shell; setting a project alongside an agent address prevents implicitly routed traces from being recorded

The agent ID is a lowercase slug, not a UUID. Use the ID shown in LangSmith rather than the agent's display name. Set `LANGSMITH_ENDPOINT` to your account's region if needed, using the EU example above for EU accounts. After changing `.env`, restart the notebook kernel so the new settings take effect.

For more information on LangSmith, see our docs [here](https://docs.langchain.com/langsmith/home).

**Note:** If you enable LangSmith tracing by setting `LANGSMITH_TRACING=true` in your .env file, make sure you have a valid `LANGSMITH_API_KEY` set. The environment verification script (`env_utils.py`) will warn you if tracing is enabled without a valid key.

### Environment Variables
This project uses the [dotenv](https://pypi.org/project/python-dotenv) module to read key-value pairs from the .env file and set them in the environment in the Jupyter notebooks. They do not need to be set globally in your system environment.

**Note:** If you have API keys already set in your system environment, they may conflict with the ones in your .env file. The `env_utils.py` verification script will detect and warn you about such conflicts. By default, `load_dotenv()` does not override existing environment variables.

### Development Environment
We use [Jupyter](https://jupyter.org/) notebooks. The Jupyter package is installed in the virtual environment and can be run as described above. Jupyter notebooks can also be edited and run in VSCode or other VSCode variants such as Windsurf or Cursor.
