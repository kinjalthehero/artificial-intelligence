# Stock AI Analyst

A multi-agent stock analysis app that generates comprehensive investment reports using AI. Enter any stock ticker and get a detailed analysis powered by two AI agents working together.

**[Try the Live App](https://stock-analysis-ai-web-app.streamlit.app/)**

## How It Works

The app uses **CrewAI** to orchestrate two AI agents that collaborate on each analysis:

1. **Stock Analyst Agent** — Gathers the latest news (via SerpAPI) and financial data (via Yahoo Finance), then provides insights on price trends and market sentiment
2. **Stock Report Writer Agent** — Takes the analyst's findings and writes a clear, concise investment report

```
User enters ticker (e.g. AAPL)
        |
        v
+-----------------------+
|  Analyst Agent        |
|  - Fetches news       |--> SerpAPI (Google News)
|  - Fetches prices     |--> Yahoo Finance (1-month data)
|  - Generates insights |
+-----------+-----------+
            |
            v
+-----------------------+
|  Writer Agent         |
|  - Reads insights     |
|  - Writes report      |--> Downloadable .txt report
+-----------------------+
```

## Features

- **Multi-Agent AI** — Two specialized agents collaborate via CrewAI
- **Real-Time Data** — Latest stock prices from Yahoo Finance and news from Google via SerpAPI
- **LLM Powered** — Uses Groq's Llama 3.3 70B model for fast inference
- **Modern UI** — Gradient hero banner, live stock metric cards, step-by-step agent progress tracking
- **Info Tabs** — Built-in Tech Stack, How to Use, and Limitations tabs for transparency
- **Downloadable Reports** — Export analysis as a text file
- **Hosted or BYOK** — Use the app owner's API keys or bring your own
- **Session Limits** — Built-in rate limiting for shared hosted keys
- **Password Protection** — Optional app password for controlled access

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI** | Streamlit |
| **Agent Framework** | CrewAI |
| **LLM** | Groq (Llama 3.3 70B Versatile) |
| **News Data** | SerpAPI (Google News) |
| **Financial Data** | yfinance (Yahoo Finance) |
| **Deployment** | Streamlit Community Cloud |

## Limitations (Free Tier)

| Service | Limit | Impact |
|---------|-------|--------|
| **Groq** | ~30 req/min, 12,000 tokens/min | "Rate limit" errors — wait 10s and retry |
| **SerpAPI** | 100 searches/month | Each analysis uses 1–2 searches |
| **Streamlit Cloud** | Sleeps after inactivity | First load may take 30–60s to wake up |
| **Llama 3.3 70B** | AI-generated content | May occasionally produce inaccurate data — verify with official sources |

## Run Locally

```bash
cd stock-ai-app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run stock_ai_app.py
```

### Set up API keys

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your keys:

```toml
GROQ_API_KEY = "your_groq_key"
SERPAPI_KEY = "your_serpapi_key"
```

Get free keys at:
- [Groq Console](https://console.groq.com/keys)
- [SerpAPI](https://serpapi.com/)

## Deploy on Streamlit Community Cloud

1. Push to GitHub
2. Create a new app on [share.streamlit.io](https://share.streamlit.io)
3. Set `Main file path` to `stock-ai-app/stock_ai_app.py`
4. Set Python version to **3.11** in Advanced Settings
5. Add your keys in **App settings > Secrets**
6. Deploy

## Project Files

| File | Purpose |
|------|---------|
| `stock_ai_app.py` | Main application — agents, tools, UI, and orchestration |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml.example` | Template for API keys |
| `Whisper_High_Accuracy_Transcriber.ipynb` | Bonus: OpenAI Whisper audio transcription notebook |

## Author

[Kinjal Mistry](https://github.com/kinjalthehero)
