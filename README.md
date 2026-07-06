# DealSense 🔍
### Multi-Agent AI Product Search Powered by Gemini & LangGraph

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green?style=flat)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

> **"Tell me what you need. I'll find the best deal."**
> DealSense is a conversational, multi-agent AI system that understands your product requirements, searches the live web, reads real user reviews, scores every deal by value — and explains exactly why each recommendation ranked where it did.

---

## 📸 Demo

![DealSense UI](docs/demo_screenshot.png)

---

## ✨ What Makes This Different

Most product search tools return a list and leave you to figure it out. DealSense thinks like a knowledgeable friend who did the research for you:

- **Asks clarifying questions** before searching — understands must-haves vs nice-to-haves
- **Searches the live web** across Amazon, Best Buy, Walmart, and review sites in real time
- **Reads actual user reviews** and extracts structured pros, cons, and community scores
- **Scores every deal** using a transparent weighted formula — price fit, spec match, community score
- **Explains its reasoning** — "Ranked #1 because it hits all your specs at 6% under budget with an 8.4/10 community score"
- **Runs 5 agents in parallel** — Review Analyst and Price Tracker execute simultaneously for speed

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│           Orchestrator              │  ← Gemini understands intent,
│   (clarification + spec extraction) │    asks questions, extracts specs
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           Spec Parser               │  ← Builds optimized search query
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           Web Search Agent          │  ← SerpAPI → real products
│     + Gemini relevance filter       │    Filters irrelevant results
└──────┬──────────────────────┬───────┘
       │                      │
       ▼ (parallel)           ▼ (parallel)
┌──────────────┐    ┌─────────────────┐
│   Review     │    │  Price Tracker  │  ← SQLite persistence
│   Analyst    │    │  + Alert Check  │    Price history logging
└──────┬───────┘    └────────┬────────┘
       │                     │
       └──────────┬──────────┘
                  ▼
┌─────────────────────────────────────┐
│           Deal Scorer               │  ← Weighted ranking formula
│  price_fit × 0.35 + spec × 0.35    │
│  + community_score × 0.30           │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│           Synthesizer               │  ← Gemini generates "why"
│   Top N deals + explanations        │    explanation per deal
└─────────────────┬───────────────────┘
                  ▼
         Streamlit UI 🖥️
         Ranked Deal Cards
```

**7 specialized agents. 1 orchestrator. Real products. Real reviews. Real reasoning.**

---

## 🤖 The Agent Team

| Agent | Role | Tools Used |
|-------|------|-----------|
| **Orchestrator** | Intent understanding, clarification loop, spec extraction | Gemini 2.5 Flash |
| **Spec Parser** | NLP → optimized search query string | Pure logic |
| **Web Search** | Live product search + relevance filtering | SerpAPI + Gemini |
| **Review Analyst** | Review scraping + sentiment extraction | SerpAPI + Gemini |
| **Price Tracker** | Price persistence + alert management | SQLite |
| **Deal Scorer** | Weighted ranking formula | Pure logic |
| **Synthesizer** | "Why" explanation generation | Gemini 2.5 Flash |

---

## 🛠️ Tech Stack

```
LangGraph >= 0.2      Multi-agent state graph orchestration
Gemini 2.5 Flash      LLM for reasoning, extraction, synthesis
SerpAPI               Live web + shopping search
SQLite                Price history persistence
Streamlit             Web UI
Python 3.11+          Runtime
Google Antigravity    Vibe coding IDE used to build this
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google AI Studio API key (free at [aistudio.google.com](https://aistudio.google.com))
- SerpAPI key (free tier: 100 searches/day at [serpapi.com](https://serpapi.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/DealSense.git
cd DealSense

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

### Environment Setup

```bash
# .env
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxx
SERPAPI_KEY=your_serpapi_key_here
```

### Run

```bash
# Streamlit UI (recommended)
streamlit run ui/app.py

# CLI mode
python main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
DealSense/
├── agents/
│   ├── orchestrator.py      # Intent + clarification loop
│   ├── spec_parser.py       # NLP → search query
│   ├── web_search.py        # SerpAPI + relevance filter
│   ├── review_analyst.py    # Review scraping + sentiment
│   ├── price_tracker.py     # SQLite persistence + alerts
│   ├── deal_scorer.py       # Weighted ranking formula
│   └── synthesizer.py       # "Why" explanation generation
├── tools/
│   ├── search_tool.py       # SerpAPI wrapper
│   └── sqlite_tool.py       # DB init + CRUD + alerts
├── ui/
│   └── app.py               # Streamlit two-column UI
├── data/                    # SQLite DB (git-ignored)
├── docs/                    # Documentation + screenshots
├── main.py                  # LangGraph graph + run_dealsense()
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎯 Deal Scoring Formula

DealSense ranks products using a transparent weighted formula:

```
deal_score = (price_score × 0.35) + (spec_score × 0.35) + (review_score × 0.30)

where:
  price_score    = 1 - (product_price / budget_max)
  spec_score     = matched_must_have_features / total_must_have_features  
  review_score   = community_score / 10
```

Every score is **explainable** — the UI shows the breakdown and Gemini generates a plain-English rationale for every recommendation.

---

## 🔄 Example Interaction

```
You: Find me a power bank for travel

DealSense: What's your budget? Any must-have features?

You: Under $50, must have fast charging and MagSafe

DealSense: [Searching Amazon, Best Buy, Walmart...]
           [Reading reviews from Reddit, RTINGS...]
           [Scoring 12 products...]

┌─────────────────────────────────────────┐
│ 🥇 Anker MagGo 10000mAh    $42.99      │
│ Deal Score: 87%  Community: 8.4/10     │
│ ✅ MagSafe certified, 30W fast charge  │
│ ❌ Slightly bulky at 220g              │
│ 💡 "Ranked #1 — hits every spec under  │
│    budget with the highest review score"│
└─────────────────────────────────────────┘
```

---

## 🗺️ Roadmap

- [x] Multi-agent LangGraph pipeline
- [x] Real-time web search via SerpAPI
- [x] Review sentiment extraction
- [x] Weighted deal scoring
- [x] Streamlit UI with deal cards
- [x] SQLite price persistence
- [ ] Live agent progress animation
- [ ] "Ask the Agent" follow-up chat
- [ ] Comparison table view
- [ ] Score explainability breakdown
- [ ] Streamlit Cloud deployment
- [ ] Google ADK migration

---

## 🔒 Security Notes

- Never commit `.env` — it's in `.gitignore`
- SerpAPI free tier: 100 searches/day
- Gemini free tier: generous for development use
- SQLite database is local and git-ignored

---

## 📚 Built With / Learning Context

DealSense was built in **5 days** as a hands-on agentic AI learning project using **Google Antigravity** (vibe coding IDE). It demonstrates:

- **Multi-agent orchestration** with LangGraph StateGraph
- **Tool use** via external APIs (SerpAPI, Gemini)
- **Parallel agent execution** using LangGraph's Send API
- **LLM-as-judge** for relevance filtering and sentiment extraction
- **Structured output generation** with fallback handling
- **MCP-style tool consumption** patterns

The architecture patterns directly map to enterprise agentic systems and the [Google ADK](https://google.github.io/adk-docs/) paradigm described in Google's *Agent Tools & Interoperability* whitepaper (May 2026).

---

## 🤝 Contributing

Contributions welcome. Please open an issue before submitting a PR.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built by Mohit Srivastava · Enterprise AI/Data Architect ·*
