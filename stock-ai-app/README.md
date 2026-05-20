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
- **Live Price Injection** — Real-time stock price, P/E, and analyst targets are fetched from Yahoo Finance and injected directly into agent prompts, ensuring reports always reference accurate current prices
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

## AI Prompts

The quality of the reports depends heavily on how the agents are prompted. Below are the exact prompts used — defined in [`agents.py`](agents.py).

### Agent 1: Senior Equity Research Analyst

**Role:** Senior Equity Research Analyst

**Goal:**
> Conduct thorough research on the given stock. Gather: (1) latest news — earnings, guidance, analyst upgrades/downgrades, major business events, (2) financial data — current price, 30-day trend, highs, lows, volume, (3) valuation context — where the price sits relative to its recent range and whether it appears undervalued, fairly valued, or overvalued based on the data, (4) market sentiment — bullish, bearish, or neutral with evidence. Always cite specific numbers, dates, and sources.

**Backstory:**
> You are a senior equity research analyst with 15 years of experience. You take a data-driven approach — every claim is backed by a specific number or source. You evaluate stocks the way a portfolio manager would: price action, momentum, news catalysts, and relative valuation. You clearly separate confirmed facts from speculation. You focus only on what helps an investor decide to buy, hold, or sell.

**Tools:** StockNewsSearch (SerpAPI), YahooFinanceData (yfinance)

### Agent 2: Investment Report Writer

**Role:** Investment Report Writer

**Goal:**
> Write a clear, concise investment report that a non-expert investor can act on. The report must be simple to read, avoid jargon, and end with a clear verdict. Include: valuation assessment (undervalued / fairly valued / overvalued), BUY / HOLD / SELL recommendation, price target range, and key risks. Keep it focused — no fluff, no filler.

**Backstory:**
> You are an investment report writer known for making complex analysis simple. You write for everyday investors, not Wall Street insiders. Your reports are structured, scannable, and always end with a decisive verdict. You use bullet points, bold labels, and short paragraphs. You never hedge with vague language — if the data says buy, you say buy. If it says sell, you say sell.

### Task Prompts

Each analysis runs three sequential tasks:

**Task 1 — News & Sentiment Research** (Analyst Agent)
> Research the latest news and market sentiment for {TICKER}. Find: (1) most recent earnings results — did the company beat or miss estimates? Any guidance changes? (2) analyst actions — any recent upgrades, downgrades, or price target changes? What is the consensus rating? (3) major business events — new products, partnerships, acquisitions, lawsuits, leadership changes, insider buying/selling (4) sector trends — is the industry doing well or struggling? Rate the overall sentiment as BULLISH, BEARISH, or NEUTRAL with evidence.

**Task 2 — Price Action & Valuation** (Analyst Agent)
> Analyze the financial data for {TICKER} and perform a valuation assessment. Using the LIVE DATA and your tools, analyze: (1) current price vs 30-day high/low — is it near the top or bottom of its range? (2) 30-day price trend — uptrend, downtrend, or sideways? (3) momentum — is buying pressure increasing or decreasing? (4) support level and resistance level (5) valuation verdict — based on where the price sits in its range, the P/E ratio, analyst targets, trend direction, and the news sentiment, classify the stock as: UNDERVALUED, FAIRLY VALUED, or OVERVALUED. Explain your reasoning in 2-3 sentences.

**Task 3 — Investment Report** (Writer Agent)
> Write a clean, easy-to-read investment report for {TICKER}. Follow this EXACT structure: **Recommendation: BUY / HOLD / SELL**, **Valuation: UNDERVALUED / FAIRLY VALUED / OVERVALUED**, **Price Target: $X - $Y** (3-6 month range). Then: Why this rating, What's happening (news bullets with dates), Price action, Reasons to be bullish, Risks to watch, The verdict. Keep it under 400 words. Use simple language. The price target MUST be realistic.

### Live Data Injection

Before the agents run, real-time stock data is fetched from Yahoo Finance and injected directly into every task prompt as a `LIVE DATA` block. This prevents the LLM from hallucinating prices. Example:

```
LIVE DATA for AAPL (from Yahoo Finance, fetched just now):
- Company: Apple Inc.
- Current Price: $198.50
- 30-Day Change: +3.25%
- 30-Day High: $201.30
- 30-Day Low: $189.45
- P/E Ratio (Trailing): 32.1
- 52-Week High: $220.00
- 52-Week Low: $164.08
- Analyst Mean Price Target: $215.00
- Analyst Consensus: BUY
```

## Project Structure

```
stock-ai-app/
├── stock_ai_app.py        # Streamlit entry point — wires everything together
├── config.py              # Secrets loading, env vars, session quota
├── agents.py              # CrewAI agents, task prompts, crew orchestration
├── tools/
│   ├── stock_data.py      # Yahoo Finance tool + get_stock_snapshot()
│   └── news_search.py     # SerpAPI news search tool
├── ui/
│   ├── styles.py          # CSS styles
│   ├── components.py      # Metric cards, report header, sidebar, hero, footer
│   └── pages.py           # Landing page tabs (tech stack, how to use, limits)
├── requirements.txt       # Python dependencies
└── .streamlit/
    └── secrets.toml.example  # Template for API keys
```

## Author

[Kinjal Mistry](https://github.com/kinjalthehero)
