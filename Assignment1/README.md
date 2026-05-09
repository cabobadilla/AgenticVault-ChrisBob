# CloudSync Multi-Agent Support System

**AI Bootcamp · Maven — Week 1 Assignment**
*by Christian Bobadilla*

> Build a cost-efficient, routed multi-agent customer support system for CloudSync using OpenAI Agent Builder — deployed as a full-stack web app.

**Live demo:** [agenticvault-chrisbob-production.up.railway.app](https://agenticvault-chrisbob-production.up.railway.app)

---

## The Challenge

CloudSync is a B2B SaaS company processing **15,000 support tickets/month** with wildly different complexity levels:

| Tier | Volume | Type | Example |
|---|---|---|---|
| Simple | 60% | FAQ lookups | Password reset, invoice location |
| Medium | 25% | Account & billing | Double charge, plan changes |
| Complex | 15% | Technical failures, churn risk | Data not syncing, cancellation threat |

Using a single LLM for all tickets either **overspends** (GPT-5.2 at $0.05/call on trivial FAQ questions) or **under-delivers** (GPT-5-nano at $0.001/call on high-stakes escalations). The assignment: build a routed multi-agent system that matches model cost to ticket complexity.

---

## Solution: Routed Multi-Agent Architecture

```
Incoming Ticket
      │
      ▼
 Input Screen ──► Guardrails validate ticket structure
      │
      ▼
Ticket Classifier (GPT-5-nano)
  Outputs: { "category": "simple|medium|complex", "confidence": 0.0–1.0 }
      │
      ▼
  If/Else Router
  ├── complex  ──► Escalation Handler (GPT-5.2)   ─┐
  ├── medium   ──► Billing Handler    (GPT-5-mini) ─┤
  ├── else     ──► FAQ Handler        (GPT-5-nano) ─┤
  └── conf<0.7 ──► Escalation Handler (safety)    ─┘
                                                    │
                                                    ▼
                                        Response Formatter (GPT-5-nano)
                                        Standardizes output tone & structure
```

### Agents & Model Choices

| Agent | Model | Cost/call | Purpose |
|---|---|---|---|
| Ticket Classifier | GPT-5-nano | $0.001 | Classify ticket + output confidence JSON |
| FAQ Handler | GPT-5-nano | $0.001 | Simple lookups against FAQ knowledge base |
| Billing Handler | GPT-5-mini | $0.010 | Account/billing logic with tool access |
| Escalation Handler | GPT-5.2 | $0.050 | Complex reasoning, SLA-aware, churn risk |
| Response Formatter | GPT-5-nano | $0.001 | Standardize tone across all paths |

### Cost Savings

| Approach | Blended cost/ticket | Monthly (15k tickets) |
|---|---|---|
| Single model (GPT-5.2) | $0.050 | $750 |
| This system | ~$0.0134 | ~$201 |
| **Savings** | **~73%** | **~$549/month** |

Uncertain tickets (confidence < 0.7) are routed to the Escalation Handler — no misclassification ever reaches a customer with a low-quality response.

---

## Sample Tickets Handled

| # | Subject | Classification | Handler |
|---|---|---|---|
| 1 | Can't reset my password | simple · 0.86 | FAQ Handler |
| 2 | Where can I find my invoices? | simple · 0.90 | FAQ Handler |
| 3 | Charged twice this month | medium · 0.90 | Billing Handler |
| 4 | Data not syncing for our team | medium | Billing Handler |
| 5 | Considering cancellation after repeated issues | complex · escalation | Escalation Handler |

Ticket 5 (churn risk) triggered the full Escalation Handler response: acknowledged the pattern, committed ownership, opened an urgent technical escalation, initiated billing/access audits, and promised an incident owner with a status timeline.

---

## Web App

The multi-agent system is exposed as a chat widget via a full-stack portfolio app:

```
frontend/          Vite + React 19 + TypeScript + Tailwind CSS 4
backend/           FastAPI (Python 3.11)
Dockerfile         Multi-stage build — single container for dev and prod
docker-compose.yml Local dev on :8000
```

### Architecture

- **Backend** (`/api/create-session`): proxies to OpenAI ChatKit API, keeps the API key server-side. Never exposes credentials to the browser.
- **Frontend**: React SPA with React Router. In production, FastAPI serves the compiled React build as static files with SPA fallback.
- **ChatKit**: OpenAI's `@openai/chatkit-react` React wrapper + `chatkit.js` web component loaded from the OpenAI CDN.

### Running Locally

**With Docker (identical to production):**
```bash
cp .env.example .env.local   # add OPENAI_API_KEY and CHATKIT_WORKFLOW_ID
docker compose up --build    # runs on http://localhost:8000
```

**Without Docker:**
```bash
# Terminal 1 — backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend --port 8000

# Terminal 2 — frontend
cd frontend && npm ci && npm run dev   # http://localhost:3000
```

### Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Backend | OpenAI auth |
| `CHATKIT_WORKFLOW_ID` | Backend | Agent Builder workflow ID (`wf_...`) |
| `ENVIRONMENT` | Backend | Set to `production` for secure cookies |

### Running Tests

```bash
python -m pytest backend/tests/ -v
```

---

## Deliverables

The full architecture deck with screenshots of each ticket being handled is at [CloudSync_Agent_Deck_v3.pdf](CloudSync_Agent_Deck_v3.pdf).

The original assignment brief is at [Week-201-20Assignment.pdf](Week-201-20Assignment.pdf).

---

## Stack

OpenAI Agent Builder · OpenAI ChatKit · FastAPI · React 19 · Vite · Tailwind CSS 4 · Docker · Railway
