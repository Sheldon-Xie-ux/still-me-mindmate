# GitHub Upload Guide

## Project

Still Me / MindMate is a local web MVP for testing AI-native human judgment protection. It includes:

- React + Vite frontend
- FastAPI backend
- Local SQLite-backed demo state
- MindMate AutoResearch research lab
- Obsidian/NotebookLM-style research knowledge base

## What To Upload

Upload the clean package folder or zip generated for GitHub. Do not upload local dependency/runtime folders such as:

- `frontend/node_modules`
- `backend/.venv`
- `backend/harmonymind.db`
- `frontend/dist`
- `.pytest_cache`
- `*.egg-info`

These are excluded by `.gitignore` and by the generated package zip.

## Local Run

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/
```

## Verification

Backend:

```bash
cd backend
.venv/bin/python -m pytest -q
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```

## Demo Positioning

This is not a general child AI assistant. The current sharp demo frame is:

> A 14-day AI-native child learning companion experiment that protects the child's own judgment before AI gives a complete answer.

