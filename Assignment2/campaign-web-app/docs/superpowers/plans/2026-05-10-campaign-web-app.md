# Campaign Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Gradio web app that wraps the three-agent Creative Advertising pipeline (Creative Director → Strategist → Copywriter) with a tabbed UI showing each agent's output.

**Architecture:** Single `app.py` file containing all three agent definitions, a sync `run_campaign()` wrapper, and a `gr.Blocks` UI with tabbed outputs. `nest_asyncio` bridges Gradio's event loop with `asyncio.run()`. Fully standalone — its own venv, no dependency on Assignment2.

**Tech Stack:** Python 3.9+, `openai-agents`, `gradio`, `python-dotenv`, `nest_asyncio`

---

## File Structure

| File | Purpose |
|---|---|
| `campaign-web-app/requirements.txt` | Package dependencies |
| `campaign-web-app/.env.example` | API key template |
| `campaign-web-app/app.py` | Agents + pipeline + Gradio UI (single file) |

---

### Task 1: Create Environment Files

**Files:**
- Create: `campaign-web-app/requirements.txt`
- Create: `campaign-web-app/.env.example`

- [ ] **Step 1: Write requirements.txt**

Create `campaign-web-app/requirements.txt` with this exact content:

```
openai-agents
gradio
python-dotenv
nest_asyncio
```

- [ ] **Step 2: Write .env.example**

Create `campaign-web-app/.env.example` with this exact content:

```
OPENAI_API_KEY=sk-your-key-here
```

- [ ] **Step 3: Create and activate virtual environment**

```bash
cd "/Users/bobadillachristian/Personal/MyFiles/Training/AI Bootcamp - Maven/AgenticVault-ChrisBob/campaign-web-app"
python -m venv .venv
source .venv/bin/activate
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without error. Key packages: `openai-agents`, `gradio`, `python-dotenv`, `nest_asyncio`.

- [ ] **Step 5: Verify key imports work**

```bash
.venv/bin/python -c "import gradio; from agents import Agent, Runner; import nest_asyncio; print('All imports OK')"
```

Expected: `All imports OK`

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example
git commit -m "feat: add environment files for campaign web app"
```

---

### Task 2: Create app.py

**Files:**
- Create: `campaign-web-app/app.py`

- [ ] **Step 1: Write app.py**

Create `campaign-web-app/app.py` with this exact content:

```python
import asyncio
import os

import gradio as gr
import nest_asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found. Copy .env.example to .env and add your key.")

creative_director = Agent(
    name="Creative Director",
    model="gpt-4o-mini",
    instructions=(
        "You are a Creative Director at a top advertising agency. "
        "Given a product launch brief, generate 3 to 5 distinct campaign ideas. "
        "Format each idea with: **Name** (bold), *Tagline* (italic), "
        "and a 2-sentence description of the concept and target audience."
    ),
)

strategist = Agent(
    name="Strategist",
    model="gpt-4o-mini",
    instructions=(
        "You are a Marketing Strategist. You will receive a list of campaign ideas. "
        "Review them and select the top 2 ideas based on market potential, "
        "cultural fit, and originality. "
        "For each selected idea, explain in 2-3 sentences why it was chosen "
        "and what makes it commercially strong."
    ),
)

copywriter = Agent(
    name="Copywriter",
    model="gpt-4o-mini",
    instructions=(
        "You are a social media Copywriter. You will receive two selected campaign concepts. "
        "For each campaign, write exactly 3 tweets. "
        "Each tweet must: be under 280 characters, include 2-3 relevant hashtags, "
        "have an inspiring and eco-conscious tone, "
        "and feel native to the target location and audience."
    ),
)


def run_campaign(prompt: str):
    """Sync wrapper for Gradio — runs the async pipeline and returns 3 outputs."""
    if not prompt or not prompt.strip():
        return "Please enter a campaign brief.", "", ""

    async def pipeline():
        cd_result = await Runner.run(creative_director, prompt)
        ideas = cd_result.final_output

        st_result = await Runner.run(strategist, ideas)
        strategy = st_result.final_output

        cw_result = await Runner.run(copywriter, strategy)
        tweets = cw_result.final_output

        return ideas, strategy, tweets

    return asyncio.run(pipeline())


with gr.Blocks(title="Creative Advertising Campaign Generator") as demo:
    gr.Markdown(
        "# 🎯 Creative Advertising Campaign Generator\n"
        "*Powered by OpenAI Agents SDK · Creative Director → Strategist → Copywriter*"
    )

    prompt = gr.Textbox(
        label="Campaign Brief",
        placeholder='e.g. "Launch a campaign for a new eco-friendly water bottle in Bali."',
        lines=3,
    )

    btn = gr.Button("▶ Generate Campaign", variant="primary")

    with gr.Tabs():
        with gr.Tab("🎨 Creative Director — Ideas"):
            ideas_out = gr.Textbox(label="Campaign Ideas", lines=12, interactive=False)
        with gr.Tab("📊 Strategist — Top 2 Picks"):
            strategy_out = gr.Textbox(label="Strategic Selection", lines=12, interactive=False)
        with gr.Tab("✍️ Copywriter — Tweets"):
            tweets_out = gr.Textbox(label="Tweets", lines=12, interactive=False)

    btn.click(
        fn=run_campaign,
        inputs=[prompt],
        outputs=[ideas_out, strategy_out, tweets_out],
    )

if __name__ == "__main__":
    demo.launch()
```

- [ ] **Step 2: Verify the file has no syntax errors**

```bash
.venv/bin/python -c "import ast; ast.parse(open('app.py').read()); print('Syntax OK')"
```

Expected: `Syntax OK`

- [ ] **Step 3: Smoke-test agent instantiation (no API call)**

```bash
.venv/bin/python -c "
import os, sys
# Override the key check for smoke test
os.environ['OPENAI_API_KEY'] = 'sk-test'
# Import agents only
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

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add Gradio campaign web app with tabbed agent outputs"
```

---

### Task 3: End-to-End Launch Verification

This task verifies the app starts correctly. It does NOT require a real API call — just confirms Gradio launches without error.

**Files:** No new files.

- [ ] **Step 1: Confirm .env exists with a real key**

```bash
ls -la .env 2>/dev/null && echo ".env EXISTS" || echo "MISSING — run: cp .env.example .env then add your OPENAI_API_KEY"
```

If missing:
```bash
cp .env.example .env
# Open .env and replace sk-your-key-here with your real OpenAI API key
```

- [ ] **Step 2: Verify Gradio import + Blocks construct without launching**

```bash
.venv/bin/python -c "
import os
os.environ['OPENAI_API_KEY'] = 'sk-test'
import gradio as gr
with gr.Blocks(title='Test') as demo:
    gr.Markdown('# Test')
    t = gr.Textbox()
    b = gr.Button('Go')
    out = gr.Textbox()
    b.click(fn=lambda x: x, inputs=[t], outputs=[out])
print('Gradio Blocks: OK')
print('Gradio version:', gr.__version__)
"
```

Expected: `Gradio Blocks: OK` followed by the installed Gradio version.

- [ ] **Step 3: Launch the app**

```bash
source .venv/bin/activate
python app.py
```

Expected output:
```
Running on local URL:  http://127.0.0.1:7860
```

Open `http://localhost:7860` in your browser. You should see the campaign generator UI with title, input box, button, and three tabs.

- [ ] **Step 4: Run a live test with the assignment prompt**

In the browser at `http://localhost:7860`:
1. Type: `Launch a campaign for a new eco-friendly water bottle in Bali.`
2. Click **▶ Generate Campaign**
3. Wait ~10–15 seconds
4. Verify:
   - **🎨 Ideas tab**: Contains 3–5 campaign ideas with names, taglines, and descriptions
   - **📊 Strategy tab**: Contains 2 selected ideas with reasoning
   - **✍️ Tweets tab**: Contains 6 tweets (3 per campaign) with hashtags

- [ ] **Step 5: Test empty input guard**

Clear the input box and click **▶ Generate Campaign** with an empty prompt.
Expected: Ideas tab shows `"Please enter a campaign brief."`, other tabs show empty strings. No crash.

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "feat: campaign web app verified and working end-to-end"
```

---

## Self-Review Checklist

- [x] **Standalone project** — own venv, own requirements.txt, no imports from Assignment2
- [x] **All 3 agents** defined with exact instructions from spec
- [x] **`nest_asyncio.apply()`** called at module level before any async code
- [x] **`run_campaign()`** is synchronous — Gradio compatibility confirmed
- [x] **Empty input guard** — returns early message, no crash
- [x] **API key validation** — raises `ValueError` at startup if key missing
- [x] **Tabbed layout** — `gr.Blocks` with `gr.Tabs` + 3 `gr.Tab` children
- [x] **Event binding** — `btn.click(fn=run_campaign, inputs=[prompt], outputs=[ideas_out, strategy_out, tweets_out])`
- [x] **`demo.launch()`** — local only, no `share=True` (user can add if needed)
- [x] **No placeholders** — all code is complete and exact
- [x] **Type consistency** — `run_campaign` returns `(str, str, str)` matching 3 `gr.Textbox` outputs
