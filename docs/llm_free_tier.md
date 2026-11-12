# Free-tier LLM API providers
The best free-tier LLM API providers fall into two categories: first-party model labs (offering native multimodal and frontier models) and third-party inference aggregators (offering ultra-fast open-weight models).

Most require no credit card to start, though nearly all enforce strict rate limits and log free-tier prompts for model training unless you opt out or upgrade. 

## Top Free LLM API Providers in 2026 Compared
|Provider	|Notable Free Models	|Free Rate Limits / Quota	|Best For	|Key Catch|
|:---|:---|:---|:---|:---|
|Google AI Studio	|Gemini 3.8 Flash, 3.6 Flash, 3.5 Flash-Lite, 2.5 Pro, Gemma 4	|Project-level RPM, TPM, and RPD caps (resets midnight PT)	|Multimodal tasks, huge context windows, and sustained prototyping	|Prompts are logged for training outside EEA/UK/Switzerland|
|Groq	|Llama 3.3 70B, Llama 3.1 8B, GPT-OSS 120B, Qwen 3.8 27B, Whisper v3	|30 RPM, 1,000–14,400 RPD, 6K–8K TPM	|Ultra-low-latency inference and real-time voice/chat apps	|Strict per-minute token caps restrict large context prompts|
|Mistral La Plateforme	|Mistral Large 3, Mistral Medium 3.5, Small 4, Codestral	|~1 RPS (60 RPM) and 500K TPM on the free Experiment tier	|High token throughput, European compliance, and coding	|Free-tier prompts may be used for training unless you opt out|
|OpenRouter	|25+ rotating :free routes (Gemma 4, Nemotron 3.5, Ernie 5.5)	|20 RPM; 50 RPD (free) or 1,000 RPD (with $10 one-time credit deposit)	|Testing dozens of models through one OpenAI-compatible SDK	|Free models rotate frequently and providers log prompts|
|Cloudflare Workers AI	|Qwen 3.8 27B, Llama 3.x/4, Mistral Small, Whisper, BGE embeddings	|10,000 Neurons/day (~150–300 RPM depending on model)	|Full-stack serverless apps combining LLMs with vector search	|Daily Neuron pool drains quickly on larger 27B+ models|
|Cerebras	|Qwen 3 235B, Llama 3.3 70B, Llama 3.1 8B	|Generous daily token and RPM allowances (no credit card)	|Blazing-fast wafer-scale inference on massive open models	|Smaller catalog focused strictly on text generation|
|NVIDIA NIM	|Nemotron Ultra, DeepSeek, Llama, Qwen variants	|~40 RPM (~1,000 RPD) on free developer endpoints	|Evaluating enterprise and massive reasoning models	|Strictly licensed for evaluation and prototyping, not production|

## Other Worthwhile Free Options
* GitHub Models. Free for anyone with a GitHub account to prototype with OpenAI, Llama, Phi, and Mistral models directly inside GitHub workflows.
* Cohere Trial API. Provides free access to Command A, Command R+, and enterprise embedding/rerank models capped at 20 RPM and 1,000 calls per month for non-commercial use.
* Kilo Code & No-Account Routers. Services like Kilo Code offer anonymous free routing (kilo-auto/free) with up to 200 requests/hour without requiring an API key or credit card, though production use is prohibited.
* DeepSeek & Alibaba Model Studio. Rather than permanent free tiers, both grant substantial one-time signup credits (e.g., 1M to 5M free tokens valid for 30–90 days) without requiring a credit card.

## Which One Should You Pick?
* For general apps and long context: Start with Google AI Studio or Mistral La Plateforme for the highest free token limits.
* For speed and high request volume: Use Groq (llama-3.1-8b-instant gives 14,400 RPD) or Cerebras.
* For model variety with zero lock-in: Use OpenRouter and deposit $10 once (which stays untouched if you stick to :free models) to unlock 1,000 daily requests. 

## References
- [Google AI Studio Free Tier Limits: What the Gemini API Allows in 2026](https://twitterapi.io/blog/google-ai-studio-free-tier-limits)
- [GitHub: LLM APIs with permanent free tiers for text inference.](https://github.com/mnfst/awesome-free-llm-apis)
- [The best free LLM APIs in 2026: a live-probed list](https://wotai.co/blog/best-free-llm-apis)

## Groq Free Tier
Groq offers a free tier with no credit card required that provides access to its hosted open-weights models and compound AI systems under strict per-minute and daily rate limits. 

You can view the live status of all endpoints on the Groq Console Supported Models page and check exact quotas in the Groq Rate Limits Documentation.

### Text & Reasoning Models
These models handle general chat, coding, reasoning, and tool calling.

|Model ID|Best For|Free Rate Limits (RPM / RPD)|Free Token Limits (TPM / TPD)|
|:---|:---|:---|:---|
|openai/gpt-oss-120b|Heavy reasoning, tool use, and prompt caching (~500 tps)|30 / 1,000|8,000 / 200,000|
|openai/gpt-oss-20b|Fast reasoning, multilingual tasks, and tool use|30 / 1,000|8,000 / 200,000|
|qwen/qwen3.8-27b|Vision, reasoning, and function calling (Preview)|30 / 1,000|8,000 / 200,000|
|qwen/qwen3.6-27b|Multimodal text and image input, thinking and non-thinking modes, tool use, and JSON mode|Not listed|Not listed|

### Audio & Speech Models
Groq provides free daily allowances for both speech-to-text transcription and text-to-speech generation.

* Speech-to-Text (whisper-large-v3 and whisper-large-v3-turbo). Both models support 20 RPM and 2,000 RPD, with an allowance of 7,200 audio-seconds per hour and 28,800 audio-seconds (8 hours) per day.
* Text-to-Speech (canopylabs/orpheus-v1-english and canopylabs/orpheus-arabic-saudi). These preview voice models allow 10 RPM, 100 RPD, 1,200 TPM, and 3,600 TPD.

### Safety & Moderation Models
Specialized lightweight classifiers are available on the free tier to filter prompts and check content safety.
* Prompt Injection Detection (meta-llama/llama-prompt-guard-2-22m and 86m). Both preview models offer 30 RPM, 14,400 RPD, 15,000 TPM, and 500,000 TPD.
* Content Moderation (openai/gpt-oss-safeguard-20b). This safety model allows 3 RPM, 1,000 RPD, 2,000 TPM, and 200,000 TPD.

### Key Free Tier Rules
* Organization-Level Quotas. Rate limits apply across your entire organization rather than per API key, so generating multiple keys will not increase your free allowance.
* Prompt Caching Savings. Cached tokens do not count toward your rate limits.
* Limits Are a Summary. The published numbers are a high-level summary and there may be exceptions. Check the limits page in your account settings (console.groq.com/settings/limits) for your exact limits.

### Groq References
- [Groq](https://console.groq.com/)
- [Groq: Suported Models](https://console.groq.com/docs/models),
- [Groq: Rate Limits](https://console.groq.com/docs/rate-limits)
- [Groq: Pricing](https://www.cloudzero.com/blog/groq-pricing/)

### OpenRouter Free Tier
OpenRouter provides zero-cost API access to dozens of free-variant models (ending in :free) with a rate limit of 20 requests per minute (RPM) and 50 to 1,000 requests per day (RPD) depending on your account's credit purchase history. 

You can browse the full live catalog on the OpenRouter Free Models Collection and verify your exact account quotas in the OpenRouter Rate Limits Documentation. 

### Free Tier Rate Limits
OpenRouter enforces strict request caps across all :free model endpoints rather than charging per token.

|Account Tier (All-Time Credits Purchased)|	Requests Per Minute (RPM)|	Requests Per Day (RPD)|	Cost Per Token|
|:---|:---|:---|:---|
|Less than $10 (No credit card required)|	20 RPM|	50 RPD|	$0.00|
|At least $10 (One-time credit top-up)|	20 RPM|	1,000 RPD|	$0.00|

### Notable Free Models
Free availability rotates frequently as providers sponsor preview and open-weight models. 

* Auto-Routing (openrouter/free). Automatically routes your prompt to an available free model that matches your request's required features, such as vision or tool calling. 
* General & Reasoning (baidu/ernie-5.5-flash-preview:free and dots-studio/dots-3-note-preview:free). Large mixture-of-experts models offering up to 1M-token context windows for research, reasoning, and multimodal tasks. 
* Coding & Agents (cohere/north-mini-code:free and recursive/flint:free). Specialized open-weight models tuned for software engineering, bug fixing, and terminal agent harnesses. 
* Multimodal & Vision (google/gemma-4-31b:free and nvidia/nemotron-3.5-super-vl:free). High-capability models supporting both text and image inputs. 
* Lightweight & Edge (liquid/lfm3-1.7b:free and nvidia/nemotron-3.5-lightning:free). Compact, high-throughput models built for fast tool calling and structured outputs.
* Embeddings & Reranking (nvidia/nemotron-3.5-embed-8b:free). Zero-cost retrieval models suited for RAG pipelines and semantic search. 

### Important Free Tier Rules
* Data Logging. Many free-tier providers log prompts and completions to train or improve their models. Avoid sending sensitive or proprietary data to :free endpoints unless you check the model's specific data policy.
* Preserved Credits. If you deposit $10 to unlock the 1,000 RPD free tier, your $10 balance remains untouched as long as you only call :free model IDs. 

### OpenRouter References
- [OpenRouter: Free](https://openrouter.ai/openrouter/free)
- [OpenRouter: Free Models](https://openrouter.ai/collections/free-models)
- [OpenRouter: Limits](https://openrouter.ai/docs/api_reference/limits)
