# Chat Application

The Week 2 application lives in one folder with separately deployable backend
and frontend projects.

```text
chat-app/
├── backend/    FastAPI + LangChain
└── frontend/   Angular 21
```

The repository-level `.venv` and `.env` are shared by the learning exercises
and the backend during local development.

## Start the backend

From the repository root:

```powershell
cd chat-app\backend
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API documentation: <http://127.0.0.1:8000/docs>

The UI contains General Chat, Template Chat, and multi-model Review Analysis.

## Start the frontend

In another terminal, from the repository root:

```powershell
cd chat-app\frontend
npm.cmd start
```

Angular development server: <http://localhost:4200>

`npm.cmd` is used because this machine's PowerShell policy blocks the
`npm.ps1` wrapper. It runs the same npm executable without requiring an
execution-policy change.
