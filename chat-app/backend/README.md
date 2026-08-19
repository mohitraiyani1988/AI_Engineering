# Multi-Model LangChain Chat Backend

FastAPI backend for two Angular application modes:

1. General conversational chat with history.
2. Template-based chat using `ChatPromptTemplate` and LCEL.
3. Parallel customer-review analysis with structured Pydantic output.

Both modes support Gemini, Groq, and Mistral through a shared LangChain model
registry. Responses are streamed as Server-Sent Events (SSE), followed by
normalized response details.

## Setup

Run these commands from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Add the API keys you want to use to `.env`. A provider without a key remains
visible in `GET /models` with `configured: false`.

Gemini uses `GEMINI_API_KEY` consistently across the repository. The Angular
origins permitted to call this backend are configured as a comma-separated
list:

```env
CORS_ALLOWED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

Add another exact origin when the frontend host or port changes. Do not use a
trailing slash in an origin.

Start the backend:

```powershell
cd chat-app\backend
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

## Catalog endpoints

### `GET /models`

Returns safe model IDs for the Angular selector. API keys are never returned.

### `GET /templates`

Returns template definitions and form fields. Angular can use this response to
render the template form dynamically.

## General chat

`POST /chat/stream`

```json
{
  "model_id": "groq-llama",
  "message": "Explain LCEL",
  "history": [
    {"role": "user", "content": "I am learning LangChain."},
    {"role": "assistant", "content": "Let's start with the basics."}
  ]
}
```

## Template-based chat

`POST /templates/explain-concept/stream`

```json
{
  "model_id": "mistral-small",
  "inputs": {
    "topic": "prompt templates",
    "experience_level": "beginner",
    "response_style": "bullet points",
    "number_of_examples": 2
  }
}
```

## Review analysis

`POST /reviews/analyze/stream`

```json
{
  "review": "Fast delivery and good packaging, but the battery lasts only two hours.",
  "model_ids": ["gemini-flash", "groq-llama", "mistral-small"],
  "strategy": "native"
}
```

Use `strategy: "native"` for each provider's structured-output integration or
`strategy: "parser"` to exercise `PydanticOutputParser`. The backend starts all
selected provider pipelines concurrently and emits `model_result` or
`model_error` as each finishes. A single provider failure does not cancel the
other results.

Every successful analysis is validated as:

```text
sentiment: positive | neutral | negative
rating: 1..5
summary: string
pros: string[]
cons: string[]
recommendation: boolean
```

## SSE events

The two streaming endpoints use the same contract.

```text
event: start
data: {"message_id":"...","mode":"general","provider":"groq",...}

event: token
data: {"message_id":"...","text":"response chunk"}

event: done
data: {"message_id":"...","details":{"input_tokens":10,...}}

event: error
data: {"message_id":"...","code":"provider_error","message":"..."}
```

The `details` object includes provider, model, input/output/total/reasoning
tokens when available, finish reason, total latency, time to first token,
stream chunk count, and raw provider metadata.

## Tests

The tests use fake LangChain chunks and make no provider API calls:

```powershell
cd chat-app\backend
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
