# Design: Campaign Web App

**Date:** 2026-05-10
**Project:** campaign-web-app — Gradio web interface for the Creative Advertising multi-agent pipeline
**Based on:** Assignment2 multi-agent system (Creative Director → Strategist → Copywriter)

---

## Overview

A standalone Python web application that wraps the three-agent advertising pipeline in a Gradio UI. Users enter a campaign brief, click Generate, and see each agent's output in a tabbed interface — Ideas, Strategy, and Tweets.

---

## Architecture

```
campaign-web-app/
├── app.py            ← agents + Gradio UI (single file, ~80 lines)
├── requirements.txt  ← openai-agents, gradio, python-dotenv, nest_asyncio
├── .env.example      ← OPENAI_API_KEY=sk-your-key-here
└── .venv/            ← isolated Python environment
```

**Pattern:** Standalone project. Agent definitions are copied from Assignment2 into `app.py` — no shared module, no dependency on the notebook. Self-contained and independently runnable.

**Runtime:** `python app.py` → Gradio launches at `http://localhost:7860`

---

## Agent Definitions (copied from Assignment2)

All three agents use `model="gpt-4o-mini"` with the same instructions as the notebook:

| Agent | Instructions summary |
|---|---|
| **Creative Director** | Generate 3–5 campaign ideas. Format: **Name**, *Tagline*, 2-sentence description. |
| **Strategist** | Select top 2 ideas. Explain reasoning (market potential, cultural fit, originality). |
| **Copywriter** | Write 3 tweets per selected campaign. Under 280 chars, 2–3 hashtags, eco-conscious tone. |

---

## Gradio UI Design

**Framework:** `gr.Blocks` (gives full layout control vs. `gr.Interface`)

**Layout:**

```
┌─────────────────────────────────────────────┐
│  🎯 Creative Advertising Campaign Generator  │
│  Powered by OpenAI Agents SDK                │
├─────────────────────────────────────────────┤
│  Campaign Brief  [text input]               │
│  [▶ Generate Campaign]                      │
├─────────────────────────────────────────────┤
│  [🎨 Ideas] [📊 Strategy] [✍️ Tweets]       │
│  ┌──────────────────────────────────────┐   │
│  │  Agent output text area (scrollable) │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Components:**
- `gr.Markdown` — title and subtitle
- `gr.Textbox` — campaign brief input (3 lines, with placeholder)
- `gr.Button` — "Generate Campaign", `variant="primary"`
- `gr.Tabs` with 3 `gr.Tab` children:
  - `🎨 Creative Director — Ideas` → `gr.Textbox(lines=12, label="Campaign Ideas")`
  - `📊 Strategist — Top 2 Picks` → `gr.Textbox(lines=12, label="Strategic Selection")`
  - `✍️ Copywriter — Tweets` → `gr.Textbox(lines=12, label="Tweets")`

**Event binding:** `btn.click(run_campaign, inputs=[prompt], outputs=[ideas_out, strategy_out, tweets_out])`

---

## Pipeline Function

```python
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

nest_asyncio.apply()
load_dotenv()

# ... agent definitions ...

def run_campaign(prompt: str):
    """Sync wrapper for Gradio — runs the async pipeline and returns 3 outputs."""
    async def pipeline():
        cd_result = await Runner.run(creative_director, prompt)
        ideas = cd_result.final_output

        st_result = await Runner.run(strategist, ideas)
        strategy = st_result.final_output

        cw_result = await Runner.run(copywriter, strategy)
        tweets = cw_result.final_output

        return ideas, strategy, tweets

    return asyncio.run(pipeline())
```

Gradio calls synchronous functions. `asyncio.run()` + `nest_asyncio.apply()` bridges the gap.

---

## Environment Setup

```bash
cd campaign-web-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add real OPENAI_API_KEY
python app.py          # opens http://localhost:7860
```

---

## Key Constraints

- `nest_asyncio.apply()` is called at module level — required because Gradio's internal loop conflicts with `asyncio.run()` inside event handlers.
- `demo.launch()` called without `share=True` — local only. User can add `share=True` to get a temporary public Gradio link.
- No streaming — all three outputs appear together when the full pipeline completes (~10–15 seconds). Streaming would require Gradio generators and complicates the tabbed design.
- No auth, no persistence — stateless demo app. Each button click runs a fresh pipeline.
