# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Monorepo of independent AI/ML projects, each in its own subdirectory with its own dependencies. Python 3.11 throughout.

## Projects

### stock-ai-app

Multi-agent stock analysis app — two CrewAI agents (analyst + writer) collaborate to produce investment reports from a stock ticker. Streamlit frontend, Groq LLM (Llama 3.3 70B), SerpAPI for news, yfinance for market data.

**Run locally:**
```bash
cd stock-ai-app
python3 -m venv venv && source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run stock_ai_app.py
```

**Secrets:** Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in `GROQ_API_KEY` and `SERPAPI_KEY`. Config lookup order: `st.secrets` then `os.environ` (see `config.py:get_config_value`).

**Architecture:**
- `stock_ai_app.py` — Streamlit entry point; wires sidebar/UI, caches LLM + agents, orchestrates analysis flow
- `agents.py` — Defines CrewAI agents (analyst, writer), task prompts, and `run_analysis()` which builds a `Crew` and calls `kickoff()`
- `tools/stock_data.py` — `YahooFinanceTool` (CrewAI tool) + `get_stock_snapshot()` (used for live data injection into prompts). Has retry logic: tries 1mo, 5d, 3mo periods then falls back to `info` dict
- `tools/news_search.py` — `StockSearchTool` wrapping SerpAPI; supports both new `Client` and legacy `GoogleSearch` APIs
- `ui/` — `components.py` (sidebar, metric cards, hero, footer), `styles.py` (CSS), `pages.py` (landing tabs)

Key pattern: real-time stock data is fetched via `get_stock_snapshot()` *before* agents run, then injected as a `LIVE DATA` text block into every task prompt to prevent LLM price hallucination.

Dollar signs in Streamlit markdown must be escaped (`\$`) — see `stock_ai_app.py:151`.

**Deploy:** Streamlit Community Cloud. Set main file path to `stock-ai-app/stock_ai_app.py`. Needs `runtime.txt` (python-3.11) and `packages.txt` for system deps.

### mental-wellness-ai-app

Conversational mental wellness chatbot. Streamlit frontend, Google Gemini LLM (via LangChain), ChromaDB for long-term conversation memory (RAG), voice I/O via SpeechRecognition + pyttsx3.

**Run locally:**
```bash
cd mental-wellness-ai-app
python3 -m venv venv && source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

**Secrets:** Requires `GOOGLE_API_KEY` in a `.env` file (loaded via python-dotenv).

**Architecture:** Single-file app (`app.py`). Uses `langchain_google_genai` for Gemini 2.5 Flash, ChromaDB vector store for similarity-searched conversation history, threaded TTS for non-blocking speech output. Crisis keyword detection appends helpline guidance to responses.

### linkedin-search-ai-app

AI job search agent — scrapes LinkedIn with Playwright, scores jobs against user skills via Gemini, stores in SQLite, emails matches via Gmail SMTP. Has both a Streamlit UI and a headless scheduler mode.

**Run locally:**
```bash
cd linkedin-search-ai-app
python3 -m venv venv && source venv/bin/activate
python3 -m pip install -r requirements.txt
playwright install --with-deps
python3 -m streamlit run app.py
```

**Run with Docker:**
```bash
docker build -t linkedin-search-ai .
docker run -itd -p 8501:8501 --env-file .env --name linkedin-search linkedin-search-ai
```

**Secrets:** Requires `GOOGLE_API_KEY`, `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER` in a `.env` file. Gmail App Password needed (2-Step Verification must be enabled).

**Architecture:**
- `app.py` — Streamlit entry point; takes skills + keyword input, orchestrates the pipeline, displays results
- `scraper.py` — Playwright headless Chromium; scrapes LinkedIn public job search, extracts up to 20 job cards
- `agent.py` — Sends each job + user skills to Gemini 2.5 Flash via LangChain; returns "Relevant/Not Relevant" + score
- `database.py` — SQLite CRUD; `jobs.db` with unique constraint on link to avoid duplicates
- `mailer.py` — Gmail SMTP sender; sends formatted email with matching job details
- `scheduler.py` — Headless mode; runs the full pipeline every 6 hours using the `schedule` library with hardcoded skills

### ollama-local-ai

Fully offline AI chat application with RAG (document Q&A). React + FastAPI full-stack app that runs entirely on localhost via Ollama. Designed for macOS with a double-click app launcher.

**Run locally:**
```bash
cd ollama-local-ai
./scripts/setup.sh   # one-time: installs Ollama, models, dependencies
./scripts/start.sh   # launches backend + opens browser
```

**Architecture:**
- `backend/app/main.py` — FastAPI entry point; serves API and built frontend as static files
- `backend/app/routers/chat.py` — SSE streaming chat endpoint with RAG integration
- `backend/app/routers/conversations.py` — Conversation CRUD + full-text search
- `backend/app/routers/documents.py` — File upload, parsing, chunking, embedding
- `backend/app/services/ollama_service.py` — Async Ollama API wrapper
- `backend/app/services/rag_service.py` — RAG pipeline: chunk, embed (nomic-embed-text), query ChromaDB
- `backend/app/services/document_parser.py` — PDF (PyMuPDF) and text extraction
- `frontend/src/` — React 19 + TypeScript + Tailwind CSS 4; custom hooks for chat streaming, conversations, documents, theme

Key pattern: chat uses Server-Sent Events for real-time token streaming. Each uploaded document gets its own ChromaDB collection (`doc_{uuid}`) for isolation. Frontend is built and served as static files by FastAPI in production.

**Stack:** FastAPI, Ollama (llama3.1:8b), ChromaDB, SQLite, React 19, TypeScript, Vite, Tailwind CSS 4.

## Development Notes

- Each project has its own `requirements.txt` — install from within the project directory, not the root
- Root `requirements.txt` is for Streamlit Cloud deployment of stock-ai-app only
- No test suite exists currently
- No linter/formatter configuration exists currently
