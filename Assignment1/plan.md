# AI Bootcamp Portfolio — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a professional bootcamp portfolio web app with a landing page, the ChatKit Customer Service Agent as Assignment 1, per-project feedback collection persisted to a JSON file, a hidden admin feedback view, Docker for local dev, and Railway as the QA/test deployment environment.

**Architecture:** Single FastAPI backend serves the REST API and the built React SPA as static files. Both local dev and Railway use the same single Docker container built from the same `Dockerfile` — no environment divergence. The `CHATKIT_WORKFLOW_ID` lives as a server-side env var only — no Vite build args needed, so the Docker image is fully portable.

**Tech Stack:** Python 3.11, FastAPI 0.114, uvicorn, httpx, pytest · Vite 7, React 19, TypeScript 5.6, React Router 7, Tailwind CSS 4 · Docker, Railway

---

## File Structure

```
(project root)/
├── plan.md
├── Dockerfile                           # Multi-stage: Node builds frontend → Python serves all
├── docker-compose.yml                   # Local dev with hot reload
├── .env.example                         # Template for required env vars
├── .gitignore
├── backend/
│   ├── pyproject.toml                   # Python package metadata + deps
│   ├── requirements.txt                 # Flat deps list for Docker layer caching
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_chatkit.py              # Unit tests for /api/create-session
│   │   └── test_feedback.py             # Unit tests for /api/feedback + /api/admin/feedback
│   └── app/
│       ├── __init__.py
│       ├── main.py                      # FastAPI entry point + static SPA mount
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── chatkit.py               # POST /api/create-session (adapted from starter)
│       │   └── feedback.py              # POST /api/feedback · GET /api/admin/feedback
│       └── data/
│           └── .gitkeep
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── postcss.config.mjs
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx                      # React Router setup
        ├── index.css
        ├── pages/
        │   ├── Landing.tsx              # Portfolio home — lists all assignments
        │   ├── ChatKitAgent.tsx         # Assignment 1 wrapper page
        │   └── FeedbackAdmin.tsx        # Hidden /admin/feedback view
        ├── components/
        │   ├── ChatKitPanel.tsx         # ChatKit widget (adapted from starter)
        │   ├── FeedbackForm.tsx         # Reusable per-project feedback form
        │   └── BackToHome.tsx           # "← Portfolio" nav link
        └── lib/
            └── chatkitSession.ts        # Session secret fetcher (adapted from starter)
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: all directories listed in the file structure above
- Create: `.gitignore`
- Create: `.env.example`
- Create: `backend/app/data/.gitkeep`
- Create: all `__init__.py` files

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p backend/app/routers backend/app/data backend/tests \
         frontend/src/pages frontend/src/components frontend/src/lib \
         docs/superpowers/plans
```

- [ ] **Step 2: Create empty Python package markers**

```bash
touch backend/__init__.py \
      backend/app/__init__.py \
      backend/app/routers/__init__.py \
      backend/tests/__init__.py \
      backend/app/data/.gitkeep
```

- [ ] **Step 3: Create `.gitignore`**

```
# Python
__pycache__/
*.pyc
.venv/
backend/app/data/feedback.json

# Node
node_modules/
frontend/dist/

# Env
.env.local
.env

# Docker
.docker/

# OS
.DS_Store
```

- [ ] **Step 4: Create `.env.example`**

```
# Backend
OPENAI_API_KEY=sk-...
CHATKIT_WORKFLOW_ID=wf_...

# Frontend (optional — backend falls back to CHATKIT_WORKFLOW_ID)
VITE_CHATKIT_WORKFLOW_ID=wf_...

# Docker Compose — backend URL seen by the Vite dev server container
VITE_API_URL=http://backend:8000
```

- [ ] **Step 5: Create `.env.local` from the example (not committed)**

```bash
cp .env.example .env.local
# Fill in OPENAI_API_KEY and CHATKIT_WORKFLOW_ID with real values
```

- [ ] **Step 6: Commit scaffolding**

```bash
git add .gitignore .env.example backend/app/data/.gitkeep \
        backend/__init__.py backend/app/__init__.py \
        backend/app/routers/__init__.py backend/tests/__init__.py
git commit -m "chore: scaffold project directory structure"
```

---

## Task 2: Backend — ChatKit Router

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/routers/chatkit.py`
- Create: `backend/tests/test_chatkit.py`

- [ ] **Step 1: Write the failing test**

`backend/tests/test_chatkit.py`:
```python
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient


def make_client():
    from backend.app.main import app
    return TestClient(app)


def test_create_session_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CHATKIT_WORKFLOW_ID", raising=False)
    client = make_client()
    response = client.post("/api/create-session", json={})
    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["error"]


def test_create_session_missing_workflow(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("CHATKIT_WORKFLOW_ID", raising=False)
    monkeypatch.delenv("VITE_CHATKIT_WORKFLOW_ID", raising=False)
    client = make_client()
    response = client.post("/api/create-session", json={})
    assert response.status_code == 400
    assert "workflow" in response.json()["error"].lower()


def test_create_session_returns_client_secret(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("CHATKIT_WORKFLOW_ID", "wf_test")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"client_secret": "cs_abc123", "expires_after": 3600}

    async def mock_post(*args, **kwargs):
        return mock_response

    with patch("httpx.AsyncClient.post", new=mock_post):
        client = make_client()
        response = client.post("/api/create-session", json={})

    assert response.status_code == 200
    assert response.json()["client_secret"] == "cs_abc123"
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd (project root)
python -m pytest backend/tests/test_chatkit.py -v 2>&1 | head -20
```

Expected: `ERROR` — `ModuleNotFoundError: No module named 'backend'`

- [ ] **Step 3: Create `backend/requirements.txt`**

```
fastapi>=0.114,<0.116
httpx>=0.27,<0.28
uvicorn[standard]>=0.36,<0.37
pytest>=8.0
```

- [ ] **Step 4: Create `backend/pyproject.toml`**

```toml
[project]
name = "bootcamp-portfolio-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.114,<0.116",
    "httpx>=0.27,<0.28",
    "uvicorn[standard]>=0.36,<0.37",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -r backend/requirements.txt
```

- [ ] **Step 6: Create `backend/app/routers/chatkit.py`**

```python
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Mapping

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

_CHATKIT_BASE = "https://api.openai.com"
_COOKIE_NAME = "chatkit_session_id"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


@router.post("/api/create-session")
async def create_session(request: Request) -> JSONResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _respond({"error": "Missing OPENAI_API_KEY environment variable"}, 500)

    body = await _read_json(request)
    workflow_id = _resolve_workflow(body)
    if not workflow_id:
        return _respond({"error": "Missing workflow id"}, 400)

    user_id, new_cookie = _resolve_user(request.cookies)
    api_base = os.getenv("CHATKIT_API_BASE") or _CHATKIT_BASE

    try:
        async with httpx.AsyncClient(base_url=api_base, timeout=10.0) as client:
            upstream = await client.post(
                "/v1/chatkit/sessions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "OpenAI-Beta": "chatkit_beta=v1",
                    "Content-Type": "application/json",
                },
                json={"workflow": {"id": workflow_id}, "user": user_id},
            )
    except httpx.RequestError as exc:
        return _respond({"error": f"Failed to reach ChatKit API: {exc}"}, 502, new_cookie)

    payload = _parse_json(upstream)
    if not upstream.is_success:
        msg = (payload.get("error") if isinstance(payload, Mapping) else None) or upstream.reason_phrase
        return _respond({"error": msg or "Upstream error"}, upstream.status_code, new_cookie)

    client_secret = payload.get("client_secret") if isinstance(payload, Mapping) else None
    if not client_secret:
        return _respond({"error": "Missing client_secret in upstream response"}, 502, new_cookie)

    return _respond(
        {"client_secret": client_secret, "expires_after": payload.get("expires_after")},
        200,
        new_cookie,
    )


def _respond(payload: Mapping[str, Any], status: int, cookie: str | None = None) -> JSONResponse:
    response = JSONResponse(payload, status_code=status)
    if cookie:
        is_prod = (os.getenv("ENVIRONMENT") or "").lower() == "production"
        response.set_cookie(
            key=_COOKIE_NAME,
            value=cookie,
            max_age=_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=is_prod,
        )
    return response


async def _read_json(request: Request) -> Mapping[str, Any]:
    raw = await request.body()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, Mapping) else {}
    except json.JSONDecodeError:
        return {}


def _resolve_workflow(body: Mapping[str, Any]) -> str | None:
    wf = body.get("workflow", {})
    wf_id = (wf.get("id") if isinstance(wf, Mapping) else None) or body.get("workflowId")
    wf_id = wf_id or os.getenv("CHATKIT_WORKFLOW_ID") or os.getenv("VITE_CHATKIT_WORKFLOW_ID")
    return wf_id.strip() if wf_id and isinstance(wf_id, str) and wf_id.strip() else None


def _resolve_user(cookies: Mapping[str, str]) -> tuple[str, str | None]:
    existing = cookies.get(_COOKIE_NAME)
    if existing:
        return existing, None
    new_id = str(uuid.uuid4())
    return new_id, new_id


def _parse_json(response: httpx.Response) -> Mapping[str, Any]:
    try:
        parsed = response.json()
        return parsed if isinstance(parsed, Mapping) else {}
    except Exception:
        return {}
```

- [ ] **Step 7: Create a stub `backend/app/main.py` so the test can import it**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import chatkit, feedback

app = FastAPI(title="AI Bootcamp Portfolio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatkit.router)
# feedback router added in Task 3
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_chatkit.py -v
```

Expected:
```
PASSED test_create_session_missing_api_key
PASSED test_create_session_missing_workflow
PASSED test_create_session_returns_client_secret
3 passed
```

- [ ] **Step 9: Commit**

```bash
git add backend/requirements.txt backend/pyproject.toml \
        backend/app/routers/chatkit.py backend/app/main.py \
        backend/tests/test_chatkit.py
git commit -m "feat: add chatkit session router with tests"
```

---

## Task 3: Backend — Feedback Router

**Files:**
- Create: `backend/app/routers/feedback.py`
- Create: `backend/tests/test_feedback.py`

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_feedback.py`:
```python
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import backend.app.routers.feedback as feedback_module


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")


def make_client():
    from backend.app.main import app
    return TestClient(app)


def test_submit_feedback_returns_201():
    client = make_client()
    response = client.post(
        "/api/feedback",
        json={"project": "chatkit-agent", "comment": "Great project!", "rating": 5},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["id"], int)


def test_submit_feedback_persists():
    client = make_client()
    client.post("/api/feedback", json={"project": "chatkit-agent", "comment": "Nice!"})
    response = client.get("/api/admin/feedback")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["feedback"][0]["comment"] == "Nice!"


def test_filter_by_project():
    client = make_client()
    client.post("/api/feedback", json={"project": "chatkit-agent", "comment": "Agent comment"})
    client.post("/api/feedback", json={"project": "other-project", "comment": "Other comment"})
    response = client.get("/api/admin/feedback?project=chatkit-agent")
    body = response.json()
    assert body["total"] == 1
    assert body["feedback"][0]["project"] == "chatkit-agent"


def test_comment_required():
    client = make_client()
    response = client.post("/api/feedback", json={"project": "chatkit-agent", "comment": ""})
    assert response.status_code == 422


def test_rating_optional():
    client = make_client()
    response = client.post(
        "/api/feedback",
        json={"project": "chatkit-agent", "comment": "No rating here"},
    )
    assert response.status_code == 201
    assert response.json()["ok"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_feedback.py -v 2>&1 | head -10
```

Expected: `ERRORS` — feedback router not yet created.

- [ ] **Step 3: Create `backend/app/routers/feedback.py`**

```python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()

DATA_FILE = Path(__file__).parent.parent / "data" / "feedback.json"


class FeedbackIn(BaseModel):
    project: str
    comment: str = Field(min_length=1, max_length=1000)
    rating: Optional[int] = Field(default=None, ge=1, le=5)


def _load() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def _save(entries: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(entries, indent=2))


@router.post("/api/feedback", status_code=201)
async def submit_feedback(item: FeedbackIn):
    entries = _load()
    entry = {
        "id": len(entries) + 1,
        "project": item.project,
        "comment": item.comment,
        "rating": item.rating,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    _save(entries)
    return {"ok": True, "id": entry["id"]}


@router.get("/api/admin/feedback")
async def list_feedback(project: Optional[str] = Query(default=None)):
    entries = _load()
    if project:
        entries = [e for e in entries if e["project"] == project]
    return {"total": len(entries), "feedback": entries}
```

- [ ] **Step 4: Add the feedback router to `backend/app/main.py`**

Replace the stub with the full `main.py`:

```python
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.routers import chatkit, feedback

app = FastAPI(title="AI Bootcamp Portfolio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatkit.router)
app.include_router(feedback.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# In production the React build lives at ./static (Dockerfile copies it there).
# StaticFiles(html=True) returns index.html for unknown paths so React Router works.
if os.path.isdir("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="spa")
```

- [ ] **Step 5: Run all backend tests**

```bash
python -m pytest backend/tests/ -v
```

Expected:
```
PASSED test_chatkit.py::test_create_session_missing_api_key
PASSED test_chatkit.py::test_create_session_missing_workflow
PASSED test_chatkit.py::test_create_session_returns_client_secret
PASSED test_feedback.py::test_submit_feedback_returns_201
PASSED test_feedback.py::test_submit_feedback_persists
PASSED test_feedback.py::test_filter_by_project
PASSED test_feedback.py::test_comment_required
PASSED test_feedback.py::test_rating_optional
8 passed
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/feedback.py backend/app/main.py \
        backend/tests/test_feedback.py
git commit -m "feat: add feedback router with persistence and admin endpoint"
```

---

## Task 4: Frontend — Foundation

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/postcss.config.mjs`
- Create: `frontend/index.html`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/lib/chatkitSession.ts`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "bootcamp-portfolio",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "@openai/chatkit-react": ">=1.1.1 <2.0.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-router-dom": "^7.0.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/react": "^19.0.8",
    "@types/react-dom": "^19.0.3",
    "@vitejs/plugin-react-swc": "^3.5.0",
    "postcss": "^8.4.47",
    "tailwindcss": "^4",
    "typescript": "^5.6.3",
    "vite": "^7.1.9"
  }
}
```

- [ ] **Step 2: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Create `frontend/vite.config.ts`**

```ts
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

const apiTarget = process.env.VITE_API_URL ?? "http://localhost:8000"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: "0.0.0.0",
    proxy: {
      "/api": { target: apiTarget, changeOrigin: true },
    },
  },
})
```

- [ ] **Step 4: Create `frontend/postcss.config.mjs`**

```mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

- [ ] **Step 5: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Bootcamp Portfolio</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create `frontend/src/index.css`**

```css
@import "tailwindcss";

:root {
  color-scheme: light dark;
}
```

- [ ] **Step 7: Create `frontend/src/main.tsx`**

```tsx
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App.tsx"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```

- [ ] **Step 8: Create `frontend/src/App.tsx`**

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom"
import Landing from "./pages/Landing"
import ChatKitAgent from "./pages/ChatKitAgent"
import FeedbackAdmin from "./pages/FeedbackAdmin"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/projects/chatkit-agent" element={<ChatKitAgent />} />
        <Route path="/admin/feedback" element={<FeedbackAdmin />} />
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 9: Create `frontend/src/lib/chatkitSession.ts`**

Adapted from the starter: workflow ID is optional — if missing, the backend reads its own `CHATKIT_WORKFLOW_ID` env var, so the Docker image needs no build-time secrets.

```ts
const readEnvString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() ? value.trim() : undefined

export const workflowId =
  readEnvString(import.meta.env.VITE_CHATKIT_WORKFLOW_ID) ?? ""

export function createClientSecretFetcher(
  workflow: string,
  endpoint = "/api/create-session"
) {
  return async (currentSecret: string | null) => {
    if (currentSecret) return currentSecret

    const body: Record<string, unknown> = {}
    if (workflow) body.workflow = { id: workflow }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    const payload = (await response.json().catch(() => ({}))) as {
      client_secret?: string
      error?: string
    }

    if (!response.ok) {
      throw new Error(payload.error ?? "Failed to create session")
    }

    if (!payload.client_secret) {
      throw new Error("Missing client_secret in response")
    }

    return payload.client_secret
  }
}
```

- [ ] **Step 10: Install frontend dependencies**

```bash
cd frontend && npm install && cd ..
```

- [ ] **Step 11: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit 2>&1 | head -20 && cd ..
```

Expected: no output (zero errors). If errors appear — they will be about missing page/component files, which is fine at this stage and will resolve as later tasks complete.

- [ ] **Step 12: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold frontend with Vite, React Router, and Tailwind"
```

---

## Task 5: Frontend — Landing Page

**Files:**
- Create: `frontend/src/pages/Landing.tsx`

- [ ] **Step 1: Create `frontend/src/pages/Landing.tsx`**

```tsx
import { Link } from "react-router-dom"

interface Project {
  id: string
  week: number
  title: string
  description: string
  tags: string[]
  path: string
}

const PROJECTS: Project[] = [
  {
    id: "chatkit-agent",
    week: 1,
    title: "Customer Service Agent",
    description:
      "AI-powered customer service chatbot built with OpenAI ChatKit and Agent Builder. Handles common queries with a managed workflow.",
    tags: ["ChatKit", "Agent Builder", "FastAPI"],
    path: "/projects/chatkit-agent",
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
            AI Bootcamp · Maven
          </p>
          <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Portfolio
          </h1>
          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Christian Bobadilla — Weekly Assignments
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-12">
        <h2 className="mb-6 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Assignments
        </h2>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PROJECTS.map((p) => (
            <Link
              key={p.id}
              to={p.path}
              className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-indigo-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-900 dark:hover:border-indigo-500"
            >
              <span className="text-xs font-medium text-slate-400">
                Week {p.week}
              </span>
              <h3 className="mt-1 text-lg font-semibold text-slate-900 transition-colors group-hover:text-indigo-600 dark:text-slate-100 dark:group-hover:text-indigo-400">
                {p.week}. {p.title}
              </h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                {p.description}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {p.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </main>

      <footer className="mx-auto max-w-5xl border-t border-slate-100 px-6 py-8 dark:border-slate-800">
        <p className="text-xs text-slate-400">
          Built with OpenAI ChatKit · FastAPI · React
        </p>
      </footer>
    </div>
  )
}
```

- [ ] **Step 2: Start dev servers and verify the landing page renders**

Terminal 1 (backend):
```bash
OPENAI_API_KEY=sk-test CHATKIT_WORKFLOW_ID=wf_test \
  uvicorn backend.app.main:app --reload --reload-dir backend --port 8000
```

Terminal 2 (frontend):
```bash
cd frontend && npm run dev
```

Open `http://localhost:3000` — should show the portfolio header and one project card.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Landing.tsx
git commit -m "feat: add portfolio landing page"
```

---

## Task 6: Frontend — ChatKit Agent Page

**Files:**
- Create: `frontend/src/components/ChatKitPanel.tsx`
- Create: `frontend/src/components/BackToHome.tsx`
- Create: `frontend/src/pages/ChatKitAgent.tsx`

- [ ] **Step 1: Create `frontend/src/components/BackToHome.tsx`**

```tsx
import { Link } from "react-router-dom"

export default function BackToHome() {
  return (
    <Link
      to="/"
      className="flex items-center gap-1.5 text-sm text-slate-500 transition-colors hover:text-indigo-600 dark:hover:text-indigo-400"
    >
      <svg
        className="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={2}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
        />
      </svg>
      Portfolio
    </Link>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/ChatKitPanel.tsx`**

Adapted from the starter — same logic, wired to our `chatkitSession.ts`.

```tsx
import { useMemo } from "react"
import { ChatKit, useChatKit } from "@openai/chatkit-react"
import { createClientSecretFetcher, workflowId } from "../lib/chatkitSession"

export function ChatKitPanel() {
  const getClientSecret = useMemo(
    () => createClientSecretFetcher(workflowId),
    []
  )

  const chatkit = useChatKit({
    api: { getClientSecret },
  })

  return (
    <div className="flex h-[75vh] w-full rounded-2xl bg-white shadow-sm dark:bg-slate-900">
      <ChatKit control={chatkit.control} className="h-full w-full" />
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/pages/ChatKitAgent.tsx`**

```tsx
import { ChatKitPanel } from "../components/ChatKitPanel"
import BackToHome from "../components/BackToHome"
import FeedbackForm from "../components/FeedbackForm"

export default function ChatKitAgent() {
  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">
          <BackToHome />
          <div className="h-5 w-px bg-slate-200 dark:bg-slate-700" />
          <div>
            <p className="text-xs text-slate-400">Assignment 1</p>
            <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100">
              Customer Service Agent
            </h1>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-8">
        <ChatKitPanel />
        <FeedbackForm project="chatkit-agent" />
      </main>
    </div>
  )
}
```

- [ ] **Step 4: Verify the page renders with a real workflow ID**

Ensure `.env.local` has `OPENAI_API_KEY` and `CHATKIT_WORKFLOW_ID` set, restart the backend, and navigate to `http://localhost:3000/projects/chatkit-agent`. The ChatKit widget should load.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/BackToHome.tsx \
        frontend/src/components/ChatKitPanel.tsx \
        frontend/src/pages/ChatKitAgent.tsx
git commit -m "feat: add Customer Service Agent page with ChatKit panel"
```

---

## Task 7: Frontend — Feedback UI

**Files:**
- Create: `frontend/src/components/FeedbackForm.tsx`
- Create: `frontend/src/pages/FeedbackAdmin.tsx`

- [ ] **Step 1: Create `frontend/src/components/FeedbackForm.tsx`**

```tsx
import { useState } from "react"

interface Props {
  project: string
}

type Status = "idle" | "loading" | "done" | "error"

export default function FeedbackForm({ project }: Props) {
  const [rating, setRating] = useState<number | null>(null)
  const [comment, setComment] = useState("")
  const [status, setStatus] = useState<Status>("idle")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!comment.trim()) return
    setStatus("loading")
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project, comment: comment.trim(), rating }),
      })
      if (!res.ok) throw new Error()
      setStatus("done")
    } catch {
      setStatus("error")
    }
  }

  if (status === "done") {
    return (
      <div className="rounded-2xl border border-green-200 bg-green-50 p-6 text-center dark:border-green-800 dark:bg-green-900/20">
        <p className="font-medium text-green-700 dark:text-green-300">
          Thank you for your feedback!
        </p>
      </div>
    )
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">
        Leave Feedback
      </h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        What do you think about this project?
      </p>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-4">
        {/* Star rating */}
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star === rating ? null : star)}
              className={`text-2xl leading-none transition-transform hover:scale-110 ${
                rating !== null && star <= rating
                  ? "text-amber-400"
                  : "text-slate-300 dark:text-slate-600"
              }`}
            >
              ★
            </button>
          ))}
        </div>

        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your thoughts…"
          rows={3}
          maxLength={1000}
          className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-indigo-400 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder-slate-500"
        />

        {status === "error" && (
          <p className="text-sm text-red-500">
            Something went wrong. Please try again.
          </p>
        )}

        <button
          type="submit"
          disabled={!comment.trim() || status === "loading"}
          className="self-start rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:opacity-50"
        >
          {status === "loading" ? "Sending…" : "Submit Feedback"}
        </button>
      </form>
    </section>
  )
}
```

- [ ] **Step 2: Create `frontend/src/pages/FeedbackAdmin.tsx`**

```tsx
import { useEffect, useState } from "react"
import BackToHome from "../components/BackToHome"

interface FeedbackEntry {
  id: number
  project: string
  comment: string
  rating: number | null
  created_at: string
}

export default function FeedbackAdmin() {
  const [entries, setEntries] = useState<FeedbackEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [project, setProject] = useState("")

  useEffect(() => {
    const url = project
      ? `/api/admin/feedback?project=${encodeURIComponent(project)}`
      : "/api/admin/feedback"
    fetch(url)
      .then((r) => r.json())
      .then((data) => setEntries(data.feedback ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [project])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <header className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-4xl items-center gap-4 px-6 py-4">
          <BackToHome />
          <div className="h-5 w-px bg-slate-200 dark:bg-slate-700" />
          <h1 className="text-base font-semibold text-slate-900 dark:text-slate-100">
            Feedback Admin
          </h1>
          <span className="ml-auto rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
            {entries.length} entries
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-8">
        {/* Filter */}
        <div className="mb-6">
          <select
            value={project}
            onChange={(e) => { setLoading(true); setProject(e.target.value) }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-indigo-400 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="">All projects</option>
            <option value="chatkit-agent">chatkit-agent</option>
          </select>
        </div>

        {loading ? (
          <p className="text-sm text-slate-400">Loading…</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-slate-400">No feedback yet.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {entries.map((e) => (
              <div
                key={e.id}
                className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
                    {e.project}
                  </span>
                  {e.rating && (
                    <span className="text-sm text-amber-400">
                      {"★".repeat(e.rating)}
                      {"☆".repeat(5 - e.rating)}
                    </span>
                  )}
                  <span className="ml-auto text-xs text-slate-400">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">
                  {e.comment}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
```

- [ ] **Step 3: Test the full feedback flow manually**

1. Navigate to `http://localhost:3000/projects/chatkit-agent`
2. Type a comment, click a star rating, submit
3. Verify the "Thank you" message appears
4. Navigate to `http://localhost:3000/admin/feedback`
5. Verify the entry appears with the correct project, rating, and timestamp

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/FeedbackForm.tsx \
        frontend/src/pages/FeedbackAdmin.tsx
git commit -m "feat: add feedback form and hidden admin view"
```

---

## Task 8: Docker Setup

Same single-container image for both local and Railway — no divergence between environments.

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: Create `Dockerfile`**

```dockerfile
# ── Stage 1: build the React frontend ──────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: run FastAPI and serve the built frontend ──────────────────────
FROM python:3.11-slim AS runtime
WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /build/dist ./static

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create `docker-compose.yml`**

Uses the same `Dockerfile` as Railway — one container, one port, no surprises.

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - path: .env.local
        required: false
    environment:
      - ENVIRONMENT=production
```

- [ ] **Step 3: Build and run locally**

```bash
docker compose up --build
```

Expected output:
```
app  | INFO:     Application startup complete.
app  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open `http://localhost:8000` — landing page renders. Navigate to the ChatKit agent — widget loads. Submit feedback — entry appears in `/admin/feedback`.

> Note: after any code change, re-run `docker compose up --build` to rebuild the image. Docker layer caching keeps rebuilds fast after the first run (`npm ci` and `pip install` layers are cached as long as their lock files don't change).

- [ ] **Step 4: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Dockerfile and docker-compose matching Railway deployment"
```

---

## Task 9: Railway Deployment

- [ ] **Step 1: Push the branch to GitHub**

```bash
git push origin main
```

- [ ] **Step 2: Create a new Railway project**

```bash
# Install Railway CLI if needed
npm install -g @railway/cli
railway login
railway init   # creates a new project, select "Empty project"
```

- [ ] **Step 3: Add the service and link to the repo**

In the Railway dashboard:
1. Click **+ New Service → GitHub Repo**
2. Select this repository
3. Railway auto-detects the `Dockerfile` — confirm

- [ ] **Step 4: Set environment variables in Railway**

In the Railway service → **Variables** tab, add:
```
OPENAI_API_KEY     = sk-...
CHATKIT_WORKFLOW_ID = wf_...
ENVIRONMENT        = production
```

- [ ] **Step 5: Deploy and verify**

Railway deploys automatically after saving variables. Wait for the build to complete (watch logs in the dashboard).

From the Railway service → **Settings → Networking**, click **Generate Domain**.

Open the generated `*.railway.app` URL and verify:
- Landing page renders
- ChatKit agent works (session creation succeeds)
- Feedback form submits
- `/admin/feedback` shows entries

- [ ] **Step 6: Confirm the health endpoint**

```bash
curl https://your-app.railway.app/health
# Expected: {"status":"ok"}
```

---

## Summary

| Layer | Local (`docker compose up --build`) | Railway (QA) |
|---|---|---|
| Image | Same `Dockerfile` | Same `Dockerfile` |
| Frontend | Built into image, served by FastAPI | Built into image, served by FastAPI |
| Backend | uvicorn in container (`localhost:8000`) | uvicorn in container |
| Secrets | `.env.local` (not committed) | Railway environment variables |
| Feedback data | `backend/app/data/feedback.json` in container (lost on restart) | Same — upgrade to Railway Volume for durability |

**Adding future assignments:** Add a new entry to the `PROJECTS` array in `Landing.tsx`, create `frontend/src/pages/NewProjectPage.tsx`, add a `<Route>` in `App.tsx`, and add a new option to the filter select in `FeedbackAdmin.tsx`.
