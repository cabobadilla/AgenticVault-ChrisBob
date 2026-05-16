import asyncio
import os
import re

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
        "For each selected idea, use **Name** (bold) as the header, "
        "then explain in 2-3 sentences why it was chosen "
        "and what makes it commercially strong."
    ),
)

copywriter = Agent(
    name="Copywriter",
    model="gpt-4o-mini",
    instructions=(
        "You are a social media Copywriter. You will receive selected campaign concepts. "
        "For each campaign, write exactly 3 tweets. "
        "Each tweet must: be under 280 characters, include 2-3 relevant hashtags, "
        "have an inspiring and eco-conscious tone, "
        "and feel native to the target location and audience."
    ),
)


def parse_blocks(text: str) -> list[dict]:
    """Split markdown output into individual blocks keyed by **Name** bold headings."""
    blocks = re.split(r'\n(?=\*\*)', text.strip())
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        name_match = re.match(r'\*\*(.+?)\*\*', block)
        if not name_match:
            continue
        name = name_match.group(1)
        tagline_match = re.search(r'\*([^*\n]+)\*', block[name_match.end():])
        tagline = tagline_match.group(1) if tagline_match else ""
        label = f"{name} — {tagline}" if tagline else name
        result.append({"label": label, "full": block})
    return result


def run_creative_director(prompt: str):
    if not prompt or not prompt.strip():
        return (
            "Please enter a campaign brief.",
            [],
            gr.update(choices=[], value=[]),
            gr.update(interactive=False),
            gr.update(interactive=False),
        )

    async def call():
        result = await Runner.run(creative_director, prompt)
        return result.final_output

    ideas_text = asyncio.run(call())
    parsed = parse_blocks(ideas_text)
    labels = [idea["label"] for idea in parsed]

    return (
        ideas_text,
        parsed,
        gr.update(choices=labels, value=labels),
        gr.update(interactive=True),
        gr.update(interactive=False),
    )


def run_strategist(selected_labels: list, ideas_data: list):
    if not ideas_data:
        return (
            "No ideas found. Please run the Creative Director first.",
            [],
            gr.update(choices=[], value=[]),
            gr.update(interactive=False),
        )
    if not selected_labels:
        return (
            "No ideas selected. Please select at least one idea.",
            [],
            gr.update(choices=[], value=[]),
            gr.update(interactive=False),
        )

    label_to_full = {idea["label"]: idea["full"] for idea in ideas_data}
    selected_text = "\n\n".join(
        label_to_full[label] for label in selected_labels if label in label_to_full
    )

    async def call():
        result = await Runner.run(strategist, selected_text)
        return result.final_output

    strategy_text = asyncio.run(call())
    parsed = parse_blocks(strategy_text)
    labels = [pick["label"] for pick in parsed]

    return (
        strategy_text,
        parsed,
        gr.update(choices=labels, value=labels),
        gr.update(interactive=True),
    )


def run_copywriter(selected_labels: list, strategy_data: list):
    if not strategy_data:
        return "No strategy found. Please run the Strategist first."
    if not selected_labels:
        return "No picks selected. Please select at least one."

    label_to_full = {pick["label"]: pick["full"] for pick in strategy_data}
    selected_text = "\n\n".join(
        label_to_full[label] for label in selected_labels if label in label_to_full
    )

    async def call():
        result = await Runner.run(copywriter, selected_text)
        return result.final_output

    return asyncio.run(call())


with gr.Blocks(title="Creative Advertising Campaign Generator") as demo:
    gr.Markdown(
        "# 🎯 Creative Advertising Campaign Generator\n"
        "*Powered by OpenAI Agents SDK · Creative Director → Strategist → Copywriter*"
    )

    ideas_data_state = gr.State([])
    strategy_data_state = gr.State([])

    prompt = gr.Textbox(
        label="Campaign Brief",
        placeholder='e.g. "Launch a campaign for a new eco-friendly water bottle in Bali."',
        lines=3,
    )

    btn_creative = gr.Button("▶ Generate Ideas", variant="primary")

    with gr.Tabs():
        with gr.Tab("🎨 Creative Director — Ideas"):
            ideas_out = gr.Textbox(label="Campaign Ideas", lines=12, interactive=False)
            ideas_selector = gr.CheckboxGroup(
                label="Select ideas to send to the Strategist (all selected by default)",
                choices=[],
                value=[],
                interactive=True,
            )
        with gr.Tab("📊 Strategist — Top 2 Picks"):
            btn_strategist = gr.Button("▶ Run Strategist", variant="primary", interactive=False)
            strategy_out = gr.Textbox(label="Strategic Selection", lines=12, interactive=False)
            strategy_selector = gr.CheckboxGroup(
                label="Select picks to send to the Copywriter (all selected by default)",
                choices=[],
                value=[],
                interactive=True,
            )
        with gr.Tab("✍️ Copywriter — Tweets"):
            btn_copywriter = gr.Button("▶ Run Copywriter", variant="primary", interactive=False)
            tweets_out = gr.Textbox(label="Tweets", lines=12, interactive=False)

    btn_creative.click(
        fn=run_creative_director,
        inputs=[prompt],
        outputs=[ideas_out, ideas_data_state, ideas_selector, btn_strategist, btn_copywriter],
    )

    btn_strategist.click(
        fn=run_strategist,
        inputs=[ideas_selector, ideas_data_state],
        outputs=[strategy_out, strategy_data_state, strategy_selector, btn_copywriter],
    )

    btn_copywriter.click(
        fn=run_copywriter,
        inputs=[strategy_selector, strategy_data_state],
        outputs=[tweets_out],
    )

if __name__ == "__main__":
    demo.launch()
