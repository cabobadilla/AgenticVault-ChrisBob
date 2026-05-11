# Design: Creative Advertising Multi-Agent System

**Date:** 2026-05-10
**Assignment:** Week 2 — Part B: Creative Advertising Multi-Agent System
**Framework:** OpenAI Agents SDK (`openai-agents` package)
**Deliverable:** Jupyter Notebook (`creative_advertising_agents.ipynb`)

---

## Overview

A three-agent sequential pipeline that automates marketing campaign ideation. Each agent's output becomes the next agent's input. The system is implemented in a single Jupyter Notebook using the OpenAI Agents SDK with standard Python `venv` + `pip`.

---

## Architecture

```
User prompt
    ↓
[Creative Director Agent]  →  3–5 campaign ideas (text)
    ↓
[Strategist Agent]         →  Top 2 ideas + reasoning (text)
    ↓
[Copywriter Agent]         →  6 tweets (3 per campaign)
```

**Pattern:** Sequential `Runner.run()` calls. The `result.final_output` string from each call is passed as the input string to the next. No handoffs, no orchestrator agent — explicit sequencing so each notebook cell shows intermediate output.

**Model:** `gpt-4o-mini` for all three agents (cost-effective for a learning project; sufficient for creative text generation).

---

## Agent Definitions

### 1. Creative Director
- **Role:** Generates 3–5 original campaign ideas for the given product and context.
- **Instructions:** "You are a Creative Director at a top advertising agency. Given a product launch brief, generate 3 to 5 distinct campaign ideas. Format each idea with: Name (bold), Tagline (italic), and a 2-sentence description of the concept and target audience."
- **Input:** User campaign prompt (e.g., "Launch a campaign for a new eco-friendly water bottle in Bali.")
- **Output:** Numbered list of formatted campaign ideas.

### 2. Strategist
- **Role:** Reviews the Creative Director's ideas, selects the top two, and explains the reasoning.
- **Instructions:** "You are a Marketing Strategist. You will receive a list of campaign ideas. Review them and select the top 2 ideas based on market potential, cultural fit, and originality. For each selected idea, explain in 2–3 sentences why it was chosen and what makes it commercially strong."
- **Input:** Creative Director's full output text.
- **Output:** Two selected ideas with strategic reasoning.

### 3. Copywriter
- **Role:** Writes 3 tweets promoting each of the two selected campaigns (6 tweets total).
- **Instructions:** "You are a social media Copywriter. You will receive two selected campaign concepts. For each campaign, write exactly 3 tweets. Each tweet must: be under 280 characters, include 2–3 relevant hashtags, have an inspiring and eco-conscious tone, and feel native to the target location and audience."
- **Input:** Strategist's full output text.
- **Output:** 6 tweets, grouped by campaign.

---

## Pipeline Implementation

```python
import asyncio
from agents import Agent, Runner

# Define agents
creative_director = Agent(name="Creative Director", model="gpt-4o-mini", instructions="...")
strategist = Agent(name="Strategist", model="gpt-4o-mini", instructions="...")
copywriter = Agent(name="Copywriter", model="gpt-4o-mini", instructions="...")

async def run_pipeline(prompt: str):
    # Step 1: Creative Director generates ideas
    cd_result = await Runner.run(creative_director, prompt)
    ideas = cd_result.final_output

    # Step 2: Strategist selects top 2
    st_result = await Runner.run(strategist, ideas)
    strategy = st_result.final_output

    # Step 3: Copywriter writes tweets
    cw_result = await Runner.run(copywriter, strategy)
    tweets = cw_result.final_output

    return ideas, strategy, tweets

# Run with test prompt
asyncio.run(run_pipeline("Launch a campaign for a new eco-friendly water bottle in Bali."))
```

---

## Notebook Structure

| Section | Cell Type | Content |
|---|---|---|
| 1a | Code | `!pip install openai-agents python-dotenv` |
| 1b | Code | Imports: `asyncio`, `os`, `dotenv`, `agents` |
| 1c | Code | `load_dotenv()` → sets `OPENAI_API_KEY` |
| 2 | Code | Define all three `Agent(...)` objects |
| 3a | Code | Run Creative Director, display `ideas` |
| 3b | Code | Run Strategist, display `strategy` |
| 3c | Code | Run Copywriter, display `tweets` |
| 4 | Markdown | Frozen sample output from one actual run |
| 5 | Markdown | One-page explanation (roles, tools, why multi-agent) |

---

## File Layout

```
Assignment2/
├── .env                                         ← OPENAI_API_KEY=sk-...
├── requirements.txt                             ← openai-agents, python-dotenv
├── creative_advertising_agents.ipynb
└── docs/superpowers/specs/
    └── 2026-05-10-creative-advertising-agents-design.md
```

---

## Environment Setup (from scratch)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux

# 2. Install dependencies
pip install openai-agents python-dotenv jupyter notebook

# 3. Create .env file
echo "OPENAI_API_KEY=sk-..." > .env

# 4. Launch Jupyter
jupyter notebook
```

---

## One-Page Explanation (Notebook Section 5)

The notebook's final markdown section must cover:

1. **Role of each agent**
   - Creative Director: Divergent thinking — generates multiple campaign concepts.
   - Strategist: Convergent thinking — filters to the commercially strongest ideas.
   - Copywriter: Execution — translates strategy into platform-ready content.

2. **Tools and functions used**
   - `Agent(name, model, instructions)` — defines each agent's persona and task.
   - `Runner.run(agent, input)` — executes an agent and returns a `RunResult`.
   - `result.final_output` — extracts the agent's text response for chaining.
   - `python-dotenv` — loads the API key from `.env` without hardcoding secrets.

3. **Why multi-agent improves the workflow**
   - Each agent has a focused role — no single prompt has to do everything.
   - Separation of concerns mirrors real creative teams (creative → strategy → copy).
   - Intermediate outputs are inspectable at each stage, making errors easy to diagnose.
   - Agents can be independently swapped or improved without changing the pipeline.

---

## Test Prompt

> "Launch a campaign for a new eco-friendly water bottle in Bali."
