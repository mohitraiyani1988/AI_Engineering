# Week 1 — AI Engineering Practical Results

## 1. Raw LLM Call

### Provider
Google Gemini

### Model
Gemini 3.5 Flash

### SDK
Google GenAI Python SDK (`google-genai`)

### Basic Flow

Python Application
→ Gemini SDK
→ Gemini API
→ Gemini Model
→ Response

### Observation

A native provider SDK is sufficient for making a basic LLM call.
LangChain is not required for a simple single-provider application.

The API response contains much more than generated text, including:

- Model version
- Generated content
- Token usage
- Reasoning/thought tokens
- Finish reason
- Response ID
- Other metadata

---

# 2. Token Experiment

## Same prompt executed multiple times

Prompt:

> Explain what an API is in one paragraph.

Observed results:

| Run | Input Tokens | Output Tokens | Thought Tokens | Total Tokens |
|---:|---:|---:|---:|---:|
| 1 | 8 | 147 | 386 | 541 |
| 2 | 8 | 181 | 344 | 533 |
| 3 | 8 | 142 | 448 | 598 |
| 4 | 8 | 179 | 436 | 623 |

### Observations

- Input token count remained constant because the prompt was unchanged.
- Output token count changed between runs.
- Thought/reasoning token count changed between runs.
- Total token consumption also changed.
- The same prompt does not necessarily produce exactly the same generation behavior.

### Learning

LLMs are probabilistic systems rather than traditional deterministic functions.

Traditional software:

    same input → same output

LLM:

    same input → potentially different output

Therefore AI applications need to be designed with variability in mind.

---

# 3. Reasoning Token Experiment

The Gemini response exposed:

- `prompt_token_count`
- `candidates_token_count`
- `thoughts_token_count`
- `total_token_count`

Example:

    Input tokens:   10
    Output tokens: 128
    Thought tokens: 383
    Total tokens:   521

### Observation

The visible answer is not necessarily representative of the total computation performed by the model.

Reasoning-capable models may consume substantial internal reasoning tokens before producing the visible answer.

### Engineering implication

AI applications need to consider:

- Token usage
- Cost
- Latency
- Reasoning effort
- Model selection
- Rate limits

Token consumption is a resource metric and should not automatically be treated as a measure of response quality.

---

# 4. Max Output Tokens Experiment

Configuration:

    max_output_tokens = 50

Observed:

    Input tokens:   22
    Output tokens:  2
    Thought tokens: 44
    Total tokens:   68
    Finish reason:  MAX_TOKENS

### Observation

`max_output_tokens` is a generation limit, not a guarantee that the model will produce that many visible output tokens.

The model consumed generation budget while reasoning and eventually reached the limit before producing the expected response.

The response was truncated:

    Response:
    Format:

### Learning

Applications should inspect the finish reason.

For example:

    STOP
    MAX_TOKENS

A production application should not blindly assume that every returned response is complete.

This connects to the AI Engineering responsibility of output validation.

---

# 5. Model Availability Experiment

The API model list included:

    gemini-2.5-flash
    gemini-3.5-flash
    gemini-3.6-flash
    ...

However, attempting to use `gemini-2.5-flash` resulted in:

    404 NOT_FOUND

The API reported that the model was no longer available to new users.

### Learning

A model appearing in a provider's model list does not necessarily mean that the model is available for inference for the current account.

AI applications should not blindly assume model availability.

Model selection and provider capability checking are part of AI engineering.

---

# 6. Temperature / Top-p / Hallucination

Status: PARKED

These experiments are temporarily postponed until another provider is added that gives us a suitable model/API for these parameters.

Planned experiments:

- Temperature
- Top-p
- Hallucination

---

# 7. Current Mental Model

An LLM is not the application.

The current architecture we have experienced is:

    User
      ↓
    Application
      ↓
    Provider SDK
      ↓
    LLM API
      ↓
    LLM
      ↓
    Response + Metadata
      ↓
    Application
      ↓
    User

The application remains responsible for things such as:

- Authentication
- Authorization
- Rate limiting
- Conversation history
- Prompt construction
- Model selection
- Token/cost management
- Output validation
- Logging
- Analytics
- External systems
- Vector database / RAG

The LLM primarily provides language generation/reasoning capability.

---

# 8. LangChain

Status: NOT STARTED

We intentionally started with the native provider SDK instead of LangChain.

Reason:

We want to understand the underlying provider API first and then experience the problems that an abstraction such as LangChain attempts to solve.

Planned flow:

    Native SDK
        ↓
    Multiple providers
        ↓
    Identify common patterns / differences
        ↓
    LangChain
        ↓
    Understand why the abstraction exists


## Provider Comparison — Initial Observation

Gemini 3.5 Flash and Groq/Llama 3.3 70B produced broadly similar
quality for the simple API-explanation prompt.

The major difference observed in this experiment was latency:
Groq/Llama 3.3 70B was significantly faster.

Therefore, a simple prompt is not sufficient to determine which
model is better. Model evaluation should use multiple workloads
such as reasoning, coding, architecture, and instruction following.

## Exercise 3 — LangChain

### Why was LangChain introduced?

Different LLM providers expose different SDKs and APIs.

For example, Gemini uses:

    client.models.generate_content(...)

while Groq uses:

    client.chat.completions.create(...)

LangChain provides a common abstraction over these providers.

With LangChain, both providers can be called using:

    llm.invoke(prompt)

The provider-specific implementation is hidden behind the LangChain integration.

### What does LangChain provide?

LangChain provides abstractions/components for:

- LLM/chat models
- Prompt templates
- Messages
- Output parsing
- Document loaders
- Retrievers
- Vector stores
- Tools
- Agents
- Chains/workflows
- Observability/integration capabilities

### Important observation

LangChain does NOT make the LLM smarter.

It is an application framework/abstraction layer that makes it easier to compose LLMs with other application components.

### Native SDK vs LangChain

For a simple application, a provider's native SDK may be simpler.

LangChain becomes more useful as the application needs multiple providers, prompts, structured outputs, retrieval, tools, agents, workflows, etc.