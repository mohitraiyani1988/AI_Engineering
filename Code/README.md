# Gemini SSE Chat Backend

A beginner-friendly FastAPI backend that streams Google Gemini responses to a client with Server-Sent Events.

The app uses a LangChain chat prompt template plus Google's `google-genai` Interactions API for local Gemini streaming.

## Project Structure

```text
llm-chat-backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes/
│   │   └── chat.py
│   └── services/
│       └── llm_service.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key to `.env`:

```text
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

## Get a Gemini API Key

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Create an API key.
4. Paste the key into `.env` as `GOOGLE_API_KEY`.

Do not commit real API keys to source control.

## Run Locally

```bash
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

## Test Streaming

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain async and await in Python"}'
```

## SSE Events

The endpoint streams these event types:

```text
event: start
data: {"message":"stream_started"}

event: token
data: {"text":"partial token here"}

event: done
data: {"message":"stream_completed","latency_ms":1234}

event: error
data: {"message":"safe error message"}
```

## How Streaming Works

1. The client sends `POST /chat/stream` with a non-empty `question`.
2. FastAPI returns a `StreamingResponse` using `text/event-stream`.
3. The route sends a `start` event.
4. `GeminiLLMService` calls Google's async Interactions API stream.
5. Each text chunk becomes a `token` event.
6. The route sends `done` with total latency when the stream completes.

## Client Disconnects

The route checks `await request.is_disconnected()` while streaming. If the client closes the connection, the server logs the disconnect and stops yielding events so it does not keep generating unnecessary output.

## Common Errors

### Missing API key

Make sure `.env` contains:

```text
GOOGLE_API_KEY=your_api_key_here
```

### Model returns 404

If Gemini returns a 404 saying the model is not available to new users, update `.env` to a currently available model:

```text
GEMINI_MODEL=gemini-3.6-flash
```

### API key returns 401

New Google AI Studio keys may start with `AQ...`. That prefix can be valid, but a `401 ACCESS_TOKEN_TYPE_UNSUPPORTED` response means Google rejected the credential for the selected project/API.

Check that the key was created from the Google AI Studio API Keys page, the project is imported into AI Studio, the Generative Language API is enabled, and the account has accepted the Gemini API terms. If the key has appeared in logs or files, create a replacement key and delete the leaked one.

### Import errors

Install dependencies inside the virtual environment:

```bash
pip install -r requirements.txt
```

### Validation error

The `question` field must be a non-empty string:

```json
{"question":"Explain FastAPI in simple words"}
```

### No streaming output in curl

Use `curl -N` so curl does not buffer the response.
