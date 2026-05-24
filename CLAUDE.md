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

## Development Notes

- Each project has its own `requirements.txt` — install from within the project directory, not the root
- Root `requirements.txt` is for Streamlit Cloud deployment of stock-ai-app only
- No test suite exists currently
- No linter/formatter configuration exists currently
