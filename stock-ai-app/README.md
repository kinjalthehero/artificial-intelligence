# Stock AI Analyst

A multi-agent stock analysis app that generates actionable investment reports with **BUY / HOLD / SELL recommendations**, **valuation assessments** (undervalued / fairly valued / overvalued), and **price target ranges**. Enter any stock ticker and get a professional-grade analysis powered by two AI agents working together.

**[Try the Live App](https://stock-analysis-ai-web-app.streamlit.app/)**

## How It Works

The app uses **CrewAI** to orchestrate two AI agents that collaborate on each analysis:

1. **Senior Equity Research Analyst** — Researches latest news, earnings reports, analyst ratings, sector trends, and financial data (P/E ratio, 52-week range, analyst targets). Identifies catalysts, support/resistance levels, assesses market sentiment, and determines if the stock is undervalued, fairly valued, or overvalued.
2. **Investment Report Writer** — Transforms the analyst's research into a structured, easy-to-read report with a clear BUY/HOLD/SELL recommendation, valuation assessment, and 3–6 month price target range. Ends with a decisive verdict.

```
User enters ticker (e.g. AAPL)
        |
        v
+-----------------------------------------+
|  Senior Analyst Agent                   |
|  - News, earnings, analyst ratings      |--> SerpAPI (Google News)
|  - Price, P/E, 52-week range, targets  |--> Yahoo Finance
|  - Sentiment: bullish / bearish         |
|  - Valuation: under / fair / overvalued |
+-------------------+---------------------+
                    |
                    v
+-----------------------------------------+
|  Investment Writer Agent                |
|  - BUY / HOLD / SELL recommendation     |
|  - Valuation assessment                 |
|  - 3-6 month price target range         |
|  - Bull case & risks                    |--> Downloadable report
|  - Decisive verdict                     |
+-----------------------------------------+
```

## Sample Report Structure

Every analysis follows this format:

1. **Recommendation** — Clear BUY, HOLD, or SELL
2. **Valuation** — Undervalued, Fairly Valued, or Overvalued
3. **Price Target** — Estimated range for the next 3–6 months
4. **Why This Rating** — 2–3 sentence rationale
5. **What's Happening** — Key news, earnings, analyst actions with dates
6. **Price Action** — Current price, 30-day trend, support/resistance, P/E context
7. **Reasons to Be Bullish** — Top reasons the stock could go higher
8. **Risks to Watch** — Top risks that could hurt the stock
9. **The Verdict** — Decisive conclusion restating recommendation, valuation, and price target

## Features

- **Actionable Reports** — Every analysis includes a BUY/HOLD/SELL recommendation, valuation assessment, and price target range
- **Valuation Analysis** — Determines if a stock is undervalued, fairly valued, or overvalued based on price action, P/E ratios, 52-week range, and analyst consensus
- **Rich Data** — P/E ratio, forward P/E, 52-week range, analyst price targets, market cap, dividend yield, and momentum signals
- **Multi-Agent AI** — Two specialized agents (Analyst + Writer) collaborate via CrewAI
- **Real-Time Data** — Latest stock prices from Yahoo Finance and news from Google via SerpAPI
- **LLM Powered** — Uses Groq's Llama 3.3 70B model for fast inference
- **Modern UI** — Gradient hero banner, live stock metric cards (price, P/E, 52-week range, analyst target), step-by-step agent progress
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
