# Chat Application Frontend

Angular 21 frontend for the FastAPI/LangChain backend.

## Features

- General chat with conversation history
- Template-based chat with backend-defined dynamic fields
- Review Analysis screen comparing structured results from multiple providers
- Gemini, Groq, and Mistral model selection
- POST response streaming through an SSE parser built on `fetch()`
- Expandable response token, latency, finish-reason, and raw metadata details

## Run

Start the backend first. Then, from this directory:

```powershell
npm.cmd start
```

Open <http://localhost:4200>. The API base URL is currently
`http://127.0.0.1:8000`.

## Verify

```powershell
npm.cmd run build
npm.cmd test -- --watch=false
```
