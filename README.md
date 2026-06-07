# HarmonyMind

HarmonyMind is a web MVP with a React/Vite frontend and a FastAPI backend.

## Demo Launch Checklist

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests/test_health.py tests/test_safety_guard.py tests/test_safe_interrupt.py -v
```

Frontend:

```bash
cd frontend
npm install
npm test -- --run src/test/app.test.tsx src/test/dashboard.test.tsx src/test/safety-notice.test.tsx
npm run build
```

Healthcheck:

```bash
curl http://localhost:8000/api/health
```

Demo script:

```text
demo/demo-script.md
```

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests/test_health.py -v
```

Frontend:

```bash
cd frontend
npm install
npm test -- --run src/test/app.test.tsx
```

Optional local app runs:

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```
