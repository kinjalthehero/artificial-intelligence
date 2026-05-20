# Stock AI Analyst

A multi-agent stock analysis app that generates actionable investment reports with **BUY / HOLD / SELL recommendations** and **price target ranges**. Enter any stock ticker and get a professional-grade analysis powered by two AI agents working together.

**[Try the Live App](https://stock-analysis-ai-web-app.streamlit.app/)**

## How It Works

The app uses **CrewAI** to orchestrate two AI agents that collaborate on each analysis:

1. **Senior Equity Research Analyst** — Researches the latest news, earnings reports, analyst ratings, sector trends, and financial data. Identifies key catalysts, support/resistance levels, and assesses market sentiment (bullish/bearish/neutral).
2. **Investment Report Writer** — Transforms the analyst's raw research into a structured report with a clear BUY/HOLD/SELL recommendation and 3–6 month price target range.

```
User enters ticker (e.g. AAPL)
        |
        v
+---------------------------------+
|  Senior Analyst Agent           |
|  - Latest news & earnings       |--> SerpAPI (Google News)
|  - Analyst ratings & catalysts  |
|  - Price action & valuation     |--> Yahoo Finance (1-month data)
|  - Sentiment: bullish/bearish   |
+---------------+-----------------+
                |
                v
+---------------------------------+
|  Investment Writer Agent        |
|  - BUY / HOLD / SELL verdict    |
|  - 3-6 month price target range |
|  - Bull case & bear case/risks  |--> Downloadable .txt report
|  - Actionable conclusion        |
+---------------------------------+
```

## Sample Report Structure

Every analysis follows this format:

1. **Recommendation** — Clear BUY, HOLD, or SELL verdict
2. **Price Target** — Estimated range for the next 3–6 months
3. **Summary** — 2–3 sentence overview
4. **Key Highlights** — Earnings, news, analyst views
5. **Financial Snapshot** — Current price, 30-day trend, support/resistance
6. **Bull Case** — Top reasons the stock could go higher
7. **Bear Case / Risks** — Top risks that could push it lower
8. **Conclusion** — Final verdict with price target restated

## Features

- **Actionable Reports** — Every analysis includes a BUY/HOLD/SELL recommendation and price target range
- **Multi-Agent AI** — Two specialized agents (Analyst + Writer) collaborate via CrewAI
- **Real-Time Data** — Latest stock prices from Yahoo Finance and news from Google via SerpAPI
- **LLM Powered** — Uses Groq's Llama 3.3 70B model for fast inference
- **Modern UI** — Gradient hero banner, live stock metric cards, step-by-step agent progress tracking
- **Info Tabs** — Built-in Tech Stack, How to Use, and Limitations tabs
- **Disclaimer** — Expandable disclaimer after every report (not financial advice, AI limitations, data freshness)
- **Downloadable Reports** — Export analysis as a text file
- **Hosted or BYOK** — Use the app owner's API keys or bring your own
- **Session Limits** — Built-in rate limiting for shared hosted keys

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
| **Llama 3.3 70B** | AI-generated content | May produce inaccurate data — verify with official sources |

> **Disclaimer:** Reports are AI-generated for informational/educational purposes only. They do not constitute financial advice. Always verify with official sources and consult a licensed financial advisor before making investment decisions.

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
