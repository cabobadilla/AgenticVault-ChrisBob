# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This is an AI Bootcamp (Maven) portfolio project. The implementation plan is in [plan.md](plan.md). As of the start of this project, the app code has not been built yet — `openai-chatkit-starter-app/` is a read-only reference clone and is not part of the deployable app.

## Architecture

Single-repo, two-layer app:

- **`backend/`** — FastAPI (Python 3.11). Exposes three API routes and, in production, serves the compiled React SPA as static files.
- **`frontend/`** — Vite + React 19 + TypeScript + Tailwind CSS 4. Single-page app with React Router. In dev, Vite proxies `/api/*` to the FastAPI backend.

**Routing model:**

| Path | Handled by |
|---|---|
| `GET /health` | FastAPI |
| `POST /api/create-session` | FastAPI — proxies to OpenAI ChatKit, keeps API key server-side |
| `POST /api/feedback` | FastAPI — appends to `backend/app/data/feedback.json` |
| `GET /api/admin/feedback` | FastAPI — reads feedback file, filterable by `?project=` |
| `/*` (all other paths) | React Router (SPA — FastAPI serves `static/index.html` as fallback in prod) |

**Key architectural constraint:** `CHATKIT_WORKFLOW_ID` is a server-side env var only. The frontend sends an empty body to `/api/create-session`; the backend resolves the workflow ID from its own environment. This means the Docker image needs no build-time secrets and is fully portable between environments.

**Environments:**

- **Local dev:** `docker compose up --build` — single container using the same `Dockerfile` as Railway. No environment divergence. After any code change, rerun with `--build`; Docker layer caching keeps rebuilds fast.
- **Railway (QA):** Same `Dockerfile`, same single container. Teacher accesses Railway — not local.

**Feedback persistence:** JSON file at `backend/app/data/feedback.json` (gitignored). Ephemeral on Railway — upgrade to a Railway Volume when durability is needed in future assignments.

**Adding a new assignment:** Add an entry to the `PROJECTS` array in `frontend/src/pages/Landing.tsx`, create `frontend/src/pages/<NewPage>.tsx`, add a `<Route>` in `frontend/src/App.tsx`, and add the project ID to the filter select in `FeedbackAdmin.tsx`.

## Commands

### Local development (Docker — identical to Railway)

```bash
docker compose up --build  # build image and run on :8000
docker compose up          # run without rebuilding (no code changes)
docker compose down        # stop
```

After any code change, rerun `docker compose up --build`. Layer caching makes rebuilds fast once `npm ci` and `pip install` layers are warm.

### Tests

```bash
# All backend tests
python -m pytest backend/tests/ -v

# Single test file
python -m pytest backend/tests/test_feedback.py -v

# Single test
python -m pytest backend/tests/test_feedback.py::test_submit_feedback_returns_201 -v
```

### Frontend build

```bash
cd frontend && npm run build    # output → frontend/dist/
```

### Frontend build (standalone, for inspection only)

```bash
cd frontend && npm run build    # output → frontend/dist/
```

## Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Backend | OpenAI auth — never exposed to frontend |
| `CHATKIT_WORKFLOW_ID` | Backend | Agent Builder workflow (`wf_...`) |
| `ENVIRONMENT` | Backend | Set to `production` to enable secure cookies |
| `VITE_API_URL` | Frontend (dev) | Vite proxy target; defaults to `http://localhost:8000` |

Copy `.env.example` → `.env.local` for local dev. `.env.local` is gitignored.

## Reference Repo

`openai-chatkit-starter-app/managed-chatkit/` is the upstream reference. The key files adapted from it are:

- `backend/app/routers/chatkit.py` ← `managed-chatkit/backend/app/main.py`
- `frontend/src/lib/chatkitSession.ts` ← `managed-chatkit/frontend/src/lib/chatkitSession.ts`
- `frontend/src/components/ChatKitPanel.tsx` ← `managed-chatkit/frontend/src/components/ChatKitPanel.tsx`
