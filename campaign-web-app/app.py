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
