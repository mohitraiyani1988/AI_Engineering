# Week 2 — LangChain Laboratory

This folder contains small experiments for learning LangChain before those ideas
are used in the chat application.

## Setup

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Add at least one provider API key to `.env`. Never commit that file.

## 1. Message types

```powershell
python .\week-2\01_messages.py
```

This creates `SystemMessage`, `HumanMessage`, `AIMessage`, and `ToolMessage`
objects locally. It does not make an API request.

## 2. Invocation methods

Choose `gemini`, `groq`, or `mistral` and one invocation method:

```powershell
python .\week-2\02_invocation_methods.py --provider gemini --method invoke
python .\week-2\02_invocation_methods.py --provider groq --method stream
python .\week-2\02_invocation_methods.py --provider mistral --method ainvoke
python .\week-2\02_invocation_methods.py --provider gemini --method astream
```

Methods:

- `invoke`: synchronous complete response
- `ainvoke`: asynchronous complete response
- `stream`: synchronous response chunks
- `astream`: asynchronous response chunks

Each run prints elapsed time plus the response metadata exposed by that provider.
