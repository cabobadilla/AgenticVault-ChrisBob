# Creative Advertising Multi-Agent System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a three-agent sequential pipeline (Creative Director → Strategist → Copywriter) delivered as a single Jupyter Notebook using the OpenAI Agents SDK.

**Architecture:** Three `Agent` objects run sequentially via `Runner.run()`. Each agent's `result.final_output` string is passed as the input to the next. `nest_asyncio` patches Jupyter's event loop so `asyncio.run()` works in cells.

**Tech Stack:** Python 3.9+, `openai-agents`, `python-dotenv`, `nest_asyncio`, `jupyter`, `notebook`

---

## File Structure

| File | Purpose |
|---|---|
| `Assignment2/requirements.txt` | Pinned package list for pip |
| `Assignment2/.env.example` | API key template — user copies to `.env` |
| `Assignment2/creative_advertising_agents.ipynb` | Main deliverable — complete notebook |

---

### Task 1: Create Environment Support Files

**Files:**
- Create: `Assignment2/requirements.txt`
- Create: `Assignment2/.env.example`

- [ ] **Step 1: Write requirements.txt**

Create `Assignment2/requirements.txt` with this exact content:

```
openai-agents
python-dotenv
nest_asyncio
jupyter
notebook
```

- [ ] **Step 2: Write .env.example**

Create `Assignment2/.env.example` with this exact content:

```
OPENAI_API_KEY=sk-your-key-here
```

- [ ] **Step 3: Verify Python version**

```bash
python --version
```
Expected: `Python 3.9.x` or higher. If lower, install Python 3.11 from python.org.

- [ ] **Step 4: Create and activate virtual environment**

```bash
cd "/Users/bobadillachristian/Personal/MyFiles/Training/AI Bootcamp - Maven/AgenticVault-ChrisBob/Assignment2"
python -m venv .venv
source .venv/bin/activate
```
Expected: Shell prompt changes to show `(.venv)`.

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```
Expected: All packages install without error. Last lines should include `Successfully installed openai-agents-...`.

- [ ] **Step 6: Verify openai-agents is importable**

```bash
python -c "from agents import Agent, Runner; print('openai-agents OK')"
```
Expected: `openai-agents OK`

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .env.example
git commit -m "feat: add environment files for creative advertising agents"
```

---

### Task 2: Create the Jupyter Notebook

**Files:**
- Create: `Assignment2/creative_advertising_agents.ipynb`

- [ ] **Step 1: Write the complete notebook file**

Create `Assignment2/creative_advertising_agents.ipynb` with this exact content:

```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "cell-header",
   "metadata": {},
   "source": [
    "# Creative Advertising Multi-Agent System\n",
    "\n",
    "**Assignment:** Week 2 — Part B  \n",
    "**Framework:** OpenAI Agents SDK  \n",
    "**Pipeline:** Creative Director → Strategist → Copywriter\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-install",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 1a — Install dependencies (run once)\n",
    "!pip install openai-agents python-dotenv nest_asyncio --quiet"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-imports",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 1b — Imports\n",
    "import asyncio\n",
    "import os\n",
    "import nest_asyncio\n",
    "from dotenv import load_dotenv\n",
    "from agents import Agent, Runner\n",
    "\n",
    "# Patch Jupyter's event loop so asyncio.run() works inside cells\n",
    "nest_asyncio.apply()\n",
    "\n",
    "print(\"Imports OK\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-env",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 1c — Load API key from .env\n",
    "load_dotenv()\n",
    "api_key = os.getenv(\"OPENAI_API_KEY\")\n",
    "if not api_key:\n",
    "    raise ValueError(\"OPENAI_API_KEY not found. Copy .env.example to .env and add your key.\")\n",
    "print(\"API key loaded.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-agents",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 2 — Define the three agents\n",
    "\n",
    "creative_director = Agent(\n",
    "    name=\"Creative Director\",\n",
    "    model=\"gpt-4o-mini\",\n",
    "    instructions=(\n",
    "        \"You are a Creative Director at a top advertising agency. \"\n",
    "        \"Given a product launch brief, generate 3 to 5 distinct campaign ideas. \"\n",
    "        \"Format each idea with: **Name** (bold), *Tagline* (italic), \"\n",
    "        \"and a 2-sentence description of the concept and target audience.\"\n",
    "    ),\n",
    ")\n",
    "\n",
    "strategist = Agent(\n",
    "    name=\"Strategist\",\n",
    "    model=\"gpt-4o-mini\",\n",
    "    instructions=(\n",
    "        \"You are a Marketing Strategist. You will receive a list of campaign ideas. \"\n",
    "        \"Review them and select the top 2 ideas based on market potential, \"\n",
    "        \"cultural fit, and originality. \"\n",
    "        \"For each selected idea, explain in 2-3 sentences why it was chosen \"\n",
    "        \"and what makes it commercially strong.\"\n",
    "    ),\n",
    ")\n",
    "\n",
    "copywriter = Agent(\n",
    "    name=\"Copywriter\",\n",
    "    model=\"gpt-4o-mini\",\n",
    "    instructions=(\n",
    "        \"You are a social media Copywriter. You will receive two selected campaign concepts. \"\n",
    "        \"For each campaign, write exactly 3 tweets. \"\n",
    "        \"Each tweet must: be under 280 characters, include 2-3 relevant hashtags, \"\n",
    "        \"have an inspiring and eco-conscious tone, \"\n",
    "        \"and feel native to the target location and audience.\"\n",
    "    ),\n",
    ")\n",
    "\n",
    "print(\"Agents defined: Creative Director, Strategist, Copywriter\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-pipeline",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 2 (cont.) — Pipeline function\n",
    "\n",
    "async def run_pipeline(prompt: str):\n",
    "    \"\"\"Run the 3-agent campaign pipeline. Returns (ideas, strategy, tweets).\"\"\"\n",
    "    cd_result = await Runner.run(creative_director, prompt)\n",
    "    ideas = cd_result.final_output\n",
    "\n",
    "    st_result = await Runner.run(strategist, ideas)\n",
    "    strategy = st_result.final_output\n",
    "\n",
    "    cw_result = await Runner.run(copywriter, strategy)\n",
    "    tweets = cw_result.final_output\n",
    "\n",
    "    return ideas, strategy, tweets\n",
    "\n",
    "print(\"Pipeline function defined.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-run-cd",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 3a — Step 1: Run Creative Director\n",
    "TEST_PROMPT = \"Launch a campaign for a new eco-friendly water bottle in Bali.\"\n",
    "\n",
    "print(\"Running Creative Director...\\n\")\n",
    "cd_result = asyncio.run(Runner.run(creative_director, TEST_PROMPT))\n",
    "ideas = cd_result.final_output\n",
    "\n",
    "print(\"=\" * 60)\n",
    "print(\"STEP 1: CREATIVE DIRECTOR — Campaign Ideas\")\n",
    "print(\"=\" * 60)\n",
    "print(ideas)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-run-st",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 3b — Step 2: Run Strategist\n",
    "print(\"Running Strategist...\\n\")\n",
    "st_result = asyncio.run(Runner.run(strategist, ideas))\n",
    "strategy = st_result.final_output\n",
    "\n",
    "print(\"=\" * 60)\n",
    "print(\"STEP 2: STRATEGIST — Top 2 Selections & Reasoning\")\n",
    "print(\"=\" * 60)\n",
    "print(strategy)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cell-run-cw",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Section 3c — Step 3: Run Copywriter\n",
    "print(\"Running Copywriter...\\n\")\n",
    "cw_result = asyncio.run(Runner.run(copywriter, strategy))\n",
    "tweets = cw_result.final_output\n",
    "\n",
    "print(\"=\" * 60)\n",
    "print(\"STEP 3: COPYWRITER — Tweets\")\n",
    "print(\"=\" * 60)\n",
    "print(tweets)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "cell-sample-output",
   "metadata": {},
   "source": [
    "## Section 4 — Sample Output\n",
    "\n",
    "> Run all cells above (Kernel → Restart & Run All) to generate live output.\n",
    "> After running, the cell outputs above serve as the sample output for submission.\n",
    "\n",
    "*(The frozen cell outputs above are produced by the test prompt: \"Launch a campaign for a new eco-friendly water bottle in Bali.\")*"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "cell-explanation",
   "metadata": {},
   "source": [
    "## Section 5 — System Explanation\n",
    "\n",
    "### Role of Each Agent\n",
    "\n",
    "| Agent | Role | Responsibility |\n",
    "|---|---|---|\n",
    "| **Creative Director** | Divergent thinker | Generates 3–5 distinct campaign ideas, each with a name, tagline, and 2-sentence description |\n",
    "| **Strategist** | Convergent thinker | Reviews all ideas and selects the top 2 based on market potential, cultural fit, and originality |\n",
    "| **Copywriter** | Executor | Translates each selected campaign into 3 ready-to-post tweets with hashtags |\n",
    "\n",
    "### Tools and Functions Used\n",
    "\n",
    "- **`Agent(name, model, instructions)`** — Defines each agent's persona, the LLM model it runs on, and its task instructions. No tools or function calls are used — these are pure text-in/text-out agents.\n",
    "- **`Runner.run(agent, input)`** — Executes an agent asynchronously given an input string. Returns a `RunResult` object containing the agent's response.\n",
    "- **`result.final_output`** — A string attribute on `RunResult` that holds the agent's final text response. This string is passed directly as the input to the next agent in the pipeline.\n",
    "- **`nest_asyncio.apply()`** — Patches Python's running event loop so that `asyncio.run()` can be called from inside Jupyter notebook cells (which already have a running event loop).\n",
    "- **`python-dotenv` / `load_dotenv()`** — Loads environment variables from a `.env` file into `os.environ`, allowing the `OPENAI_API_KEY` to be set without hardcoding secrets in the notebook.\n",
    "\n",
    "### Why a Multi-Agent Approach Improves the Workflow\n",
    "\n",
    "A single large prompt asking one LLM to generate ideas, evaluate them, and write tweets in one pass produces mediocre results — the model cannot switch creative modes mid-response without quality loss.\n",
    "\n",
    "The multi-agent pipeline improves on this in four concrete ways:\n",
    "\n",
    "1. **Focused roles** — Each agent receives instructions optimized for exactly one task. The Creative Director is not constrained by commercial concerns; the Strategist is not biased toward ideas it generated itself.\n",
    "2. **Real-team mirroring** — The Creative Director → Strategist → Copywriter sequence maps to how human advertising teams work. This makes the system's reasoning transparent and easy to audit.\n",
    "3. **Inspectable intermediate outputs** — Each agent's output is a visible string before it enters the next stage. A human can read, edit, or redirect it between steps without restarting the pipeline.\n",
    "4. **Modularity** — Any agent can be updated independently. Changing the Copywriter's tone (e.g., to LinkedIn format) requires editing only that agent's instructions, with no effect on the others.\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

- [ ] **Step 2: Verify the file is valid JSON**

```bash
python -c "import json; json.load(open('creative_advertising_agents.ipynb')); print('Valid JSON — notebook OK')"
```
Expected: `Valid JSON — notebook OK`

- [ ] **Step 3: Commit**

```bash
git add creative_advertising_agents.ipynb
git commit -m "feat: add creative advertising multi-agent notebook"
```

---

### Task 3: Smoke-Test Agent Instantiation

Before spending API credits on a live run, verify that all three agents can be instantiated with the SDK.

**Files:** No new files. Run against installed packages.

- [ ] **Step 1: Run a quick instantiation check**

```bash
python -c "
import os
os.environ.setdefault('OPENAI_API_KEY', 'sk-test')
from agents import Agent
cd = Agent(name='Creative Director', model='gpt-4o-mini', instructions='test')
st = Agent(name='Strategist', model='gpt-4o-mini', instructions='test')
cw = Agent(name='Copywriter', model='gpt-4o-mini', instructions='test')
print('Creative Director:', cd.name)
print('Strategist:', st.name)
print('Copywriter:', cw.name)
print('Smoke test: PASSED')
"
```
Expected:
```
Creative Director: Creative Director
Strategist: Strategist
Copywriter: Copywriter
Smoke test: PASSED
```

- [ ] **Step 2: Confirm .env file exists with a real key**

```bash
ls -la .env 2>/dev/null && echo ".env exists" || echo "MISSING — copy .env.example to .env and add your OPENAI_API_KEY"
```

If missing, create it:
```bash
cp .env.example .env
# Then open .env in your editor and replace sk-your-key-here with your real key
```

---

### Task 4: Run the Full Notebook and Capture Output

- [ ] **Step 1: Launch Jupyter**

```bash
source .venv/bin/activate
jupyter notebook creative_advertising_agents.ipynb
```

- [ ] **Step 2: Run all cells**

In the Jupyter UI: **Kernel → Restart & Run All**

All cells should complete without errors. Expected output per stage:
- Cell 3a: A numbered list of 3–5 campaign ideas with names, taglines, and descriptions
- Cell 3b: 2 selected ideas with strategic reasoning
- Cell 3c: 6 tweets (3 per campaign), each under 280 characters with hashtags

- [ ] **Step 3: Save the notebook with cell outputs**

In Jupyter: **File → Save** (or Cmd+S). This writes the live cell outputs into the `.ipynb` JSON, fulfilling the "sample output" requirement.

- [ ] **Step 4: Final commit**

```bash
git add creative_advertising_agents.ipynb
git commit -m "feat: complete creative advertising notebook with sample output"
```

---

## Self-Review Checklist

- [x] **3 agents defined** with exact instructions matching spec: Creative Director, Strategist, Copywriter
- [x] **Sequential pipeline** (CD → Strategist → Copywriter) via `Runner.run()` + `final_output` chaining
- [x] **Test prompt** "Launch a campaign for a new eco-friendly water bottle in Bali." included in cell-run-cd
- [x] **Jupyter Notebook** deliverable as `.ipynb` with complete JSON structure
- [x] **One-page explanation** in Section 5 covering: roles, tools/functions, why multi-agent
- [x] **Sample output** section included (Section 4)
- [x] **Environment setup from scratch** covered in Task 1 (venv, pip install, .env)
- [x] **No placeholders** — all code, instructions, and expected outputs are explicit
- [x] **Type consistency** — `result.final_output` used throughout, matching OpenAI Agents SDK `RunResult` API
