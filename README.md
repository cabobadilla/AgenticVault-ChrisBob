# 🤖 AgenticVault-ChrisBob

> My assignments and projects from the **[Agentic AI Engineering Bootcamp & Certification](https://maven.com/stemplicity/become-an-agentic-ai-engineer)** by Dr. Ryan Ahmed & Kukesh Kodess on Maven.

---

## 📚 About the Bootcamp

This bootcamp covers the full stack of Agentic AI engineering — from building single AI agents to orchestrating autonomous multi-agent teams in production. Key topics include:

- **Agentic AI Foundations** — Problem-first design, agent architectures, and design patterns
- **Single & Multi-Agent Systems** — Stateful agents with memory, tools, and handoff mechanisms using OpenAI Agents SDK
- **Orchestration Frameworks** — LangGraph, CrewAI, and AutoGen for multi-agent coordination
- **Model Context Protocol (MCP)** — Building standardized MCP servers for secure tool access
- **Agentic RAG** — Retrieval-augmented generation pipelines with autonomous planning and source verification
- **AI Coding Assistants** — Accelerating development with Claude Code and Cursor/Codex
- **Deployment & Observability** — Production monitoring, evaluation frameworks, and enterprise governance

## 🗂️ Repository Structure

```
AgenticVault-ChrisBob/
│
├── Assignment1/          # Week 1 — Multi-Agent Customer Support Routing System
│   ├── backend/          # FastAPI backend with OpenAI Agents SDK
│   ├── frontend/         # React/TypeScript UI
│   └── docs/             # Design specs and implementation plans
│
├── Assignment2/          # Week 2 — Creative Advertising Multi-Agent Pipeline
│   ├── creative_advertising_agents.ipynb  # Multi-agent notebook (Parts A & B)
│   ├── campaign-web-app/ # Gradio web UI with tabbed agent outputs
│   └── docs/             # Design specs and implementation plans
│
└── README.md
```

## 📝 Assignments

| # | Week | Topic | Folder |
|---|------|-------|--------|
| 1 | 1 | Multi-Agent Customer Support Routing System | [`Assignment1/`](./Assignment1) |
| 2 | 2 | Creative Advertising Multi-Agent Pipeline + Gradio Web App | [`Assignment2/`](./Assignment2) |
| 3 | 3 | *TBD* | *coming soon* |
| 4 | 4 | *TBD* | *coming soon* |
| 5 | 5 | *TBD* | *coming soon* |
| 6 | 6 | Capstone Project | *coming soon* |

### Assignment 2 Highlights

**Week 2 — Creative Advertising Multi-Agent Pipeline**

Built a sequential multi-agent advertising pipeline using the OpenAI Agents SDK:

- **Creative Director** → generates 3–5 distinct campaign concepts from a product brief
- **Strategist** → selects the strongest concept and defines target audience & channels
- **Copywriter** → produces final ad copy (headline, body, CTA) tailored to the strategy

Delivered in two parts:
- **Part A** — Jupyter notebook pipeline (`creative_advertising_agents.ipynb`)
- **Part B** — Gradio web app (`campaign-web-app/`) with tabbed outputs for each agent stage

## 🛠️ Tech Stack

- **Python** — Core agent logic and orchestration
- **TypeScript** — Frontend and tooling
- **Docker** — Containerized deployments
- **Frameworks** — OpenAI Agents SDK, LangGraph, CrewAI, AutoGen

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/cabobadilla/AgenticVault-ChrisBob.git
   cd AgenticVault-ChrisBob
   ```

2. Navigate to any assignment folder and follow its own README for setup instructions.

3. Most projects require Python 3.11+ and an OpenAI API key. Check each assignment for specific dependencies.

## 👤 Author

**Chris Bobadilla** — [GitHub](https://github.com/cabobadilla)

## 📄 License

This repository is for educational purposes as part of the Agentic AI Engineering Bootcamp.

---

*Built with curiosity and a lot of autonomous agents.* 🚀
