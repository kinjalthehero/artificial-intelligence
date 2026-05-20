import streamlit as st
import os
from crewai import Crew, Agent, Task, LLM
from crewai.tools import BaseTool
from typing import Any, Type
from pydantic import BaseModel, Field
import yfinance as yf
import warnings

SerpApiClient: Any = None
try:
    from serpapi import Client as SerpApiClient
except ImportError:
    SerpApiClient = None

LegacyGoogleSearch: Any = None
try:
    from serpapi import GoogleSearch as LegacyGoogleSearch
except ImportError:
    LegacyGoogleSearch = None

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Stock AI Analyst", page_icon="", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .hero {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        font-size: 1.05rem;
        opacity: 0.85;
        margin: 0;
        font-weight: 300;
    }

    .tech-pills { display: flex; gap: 8px; margin-top: 1rem; flex-wrap: wrap; }
    .tech-pill {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
    }

    .metric-row { display: flex; gap: 12px; margin: 1rem 0; }
    .metric-card {
        flex: 1;
        background: #f8f9fb;
        border: 1px solid #e8ebf0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-card .label { font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
    .metric-card .value { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin-top: 2px; }
    .metric-card .sub { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }
    .positive { color: #10b981 !important; }
    .negative { color: #ef4444 !important; }

    .report-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .report-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f3f4f6;
    }
    .report-header h2 { margin: 0; font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
    .report-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .agent-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem 1rem;
        background: #f9fafb;
        border-radius: 10px;
        margin-bottom: 8px;
        border-left: 3px solid #667eea;
    }
    .agent-step .icon { font-size: 1.2rem; }
    .agent-step .text { font-size: 0.9rem; color: #374151; font-weight: 500; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fafbfc 0%, #f0f2f5 100%);
    }
    div[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6b7280;
        font-weight: 600;
    }

    .how-it-works {
        background: #f0f4ff;
        border: 1px solid #d4deff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    .how-it-works h3 { margin: 0 0 1rem 0; font-size: 1rem; color: #374151; }
    .step-row { display: flex; gap: 16px; }
    .step {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
    }
    .step .num {
        width: 28px; height: 28px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .step .desc { font-size: 0.8rem; color: #4b5563; line-height: 1.4; }

    .info-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 10px;
    }
    .info-card h4 {
        margin: 0 0 0.6rem 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    .info-card p, .info-card li {
        font-size: 0.85rem;
        color: #4b5563;
        line-height: 1.6;
        margin: 0;
    }
    .info-card ul { padding-left: 1.2rem; margin: 0.3rem 0 0 0; }
    .info-card .tag {
        display: inline-block;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        color: #374151;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    .info-card .warn {
        background: #fef3c7;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        color: #92400e;
        margin-top: 0.6rem;
    }

    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #9ca3af;
        font-size: 0.8rem;
    }
    .footer a { color: #667eea; text-decoration: none; }
</style>
""", unsafe_allow_html=True)


def get_config_value(name: str) -> str:
    secret_value = st.secrets.get(name)
    if secret_value:
        return str(secret_value)
    return os.getenv(name, "")


def consume_hosted_quota(max_requests: int) -> bool:
    used = st.session_state.get("hosted_requests_used", 0)
    if used >= max_requests:
        return False
    st.session_state["hosted_requests_used"] = used + 1
    return True


def get_stock_snapshot(ticker_symbol: str):
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1mo")
        if hist.empty:
            return None
        info = stock.info
        current = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[0]
        change_pct = (current - prev) / prev * 100
        w52_high = info.get("fiftyTwoWeekHigh")
        w52_low = info.get("fiftyTwoWeekLow")
        return {
            "price": current,
            "change_pct": change_pct,
            "high": hist["High"].max(),
            "low": hist["Low"].min(),
            "volume": int(hist["Volume"].iloc[-1]),
            "name": info.get("shortName", ticker_symbol),
            "pe": info.get("trailingPE"),
            "fwd_pe": info.get("forwardPE"),
            "w52_high": w52_high,
            "w52_low": w52_low,
            "analyst_target": info.get("targetMeanPrice"),
            "recommendation": info.get("recommendationKey"),
        }
    except Exception:
        return None


hosted_groq_key = get_config_value("GROQ_API_KEY")
hosted_serpapi_key = get_config_value("SERPAPI_KEY")
app_password = get_config_value("APP_PASSWORD")
max_hosted_requests = int(get_config_value("MAX_REQUESTS_PER_SESSION") or 5)

with st.sidebar:
    st.markdown("## Settings")

    if app_password:
        access_password = st.text_input("App Password", type="password")
        if access_password != app_password:
            st.warning("Enter the app password to continue.")
            st.stop()

    st.markdown("## API Keys")
    hosted_keys_ready = bool(hosted_groq_key and hosted_serpapi_key)
    use_own_keys = st.toggle("Use my own API keys", value=not hosted_keys_ready)

    if use_own_keys:
        groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        serpapi_key = st.text_input("SerpAPI Key", type="password", placeholder="...")
    else:
        groq_key = hosted_groq_key
        serpapi_key = hosted_serpapi_key
        used = st.session_state.get("hosted_requests_used", 0)
        remaining = max_hosted_requests - used
        st.caption(f"Analyses remaining: **{remaining}** / {max_hosted_requests}")

    st.markdown("---")
    st.markdown(
        '<span style="font-size:0.8rem">'
        '[Get Groq Key](https://console.groq.com/keys) &nbsp;&bull;&nbsp; '
        '[Get SerpAPI Key](https://serpapi.com/)</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("## About")
    st.markdown(
        '<span style="font-size:0.82rem; color:#6b7280;">'
        "Two AI agents collaborate to research and write stock analysis reports. "
        "The <b>Analyst</b> gathers news and financial data, then the <b>Writer</b> "
        "produces a comprehensive report."
        "</span>",
        unsafe_allow_html=True,
    )

st.markdown("""
<div class="hero">
    <h1>Stock AI Analyst</h1>
    <p>AI-powered stock research &mdash; two agents collaborate to deliver comprehensive analysis in seconds</p>
    <div class="tech-pills">
        <span class="tech-pill">CrewAI</span>
        <span class="tech-pill">Groq &bull; Llama 3.3 70B</span>
        <span class="tech-pill">SerpAPI</span>
        <span class="tech-pill">Yahoo Finance</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not groq_key or not serpapi_key:
    st.info("Enter your API keys in the sidebar to get started, or use hosted keys if available.")
    st.stop()

os.environ["GROQ_API_KEY"] = groq_key
os.environ["SERPAPI_KEY"] = serpapi_key


@st.cache_resource
def get_llm(_groq_key):
    return LLM(model="groq/llama-3.3-70b-versatile", api_key=_groq_key, temperature=0.7)

llm = get_llm(groq_key)


class StockSearchInput(BaseModel):
    query: str = Field(..., description="The stock ticker or company name to search for.")

class YahooFinanceInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol to fetch data for.")

class StockSearchTool(BaseTool):
    name: str = "StockNewsSearch"
    description: str = "Search for the latest news and information about a stock using SerpAPI."
    args_schema: Type[BaseModel] = StockSearchInput

    def _run(self, query: str) -> str:
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": os.getenv("SERPAPI_KEY"),
                "tbm": "nws",
                "num": 3,
            }
            if SerpApiClient:
                client = SerpApiClient(api_key=params["api_key"])
                results = client.search({"engine": "google_news", "q": query, "num": 3})
            elif LegacyGoogleSearch:
                search = LegacyGoogleSearch(params)
                results = search.get_dict()
            else:
                return "SerpAPI client is not installed."
            news = results.get("news_results", results.get("organic_results", []))
            if not news:
                return "No news found for the given query."
            output = []
            for item in news[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", item.get("description", ""))
                output.append(f"Title: {title}: {snippet[:100]}")
            return "\n\n".join(output)
        except Exception as e:
            return f"Error fetching news: {str(e)}"


class YahooFinanceTool(BaseTool):
    name: str = "YahooFinanceData"
    description: str = "Fetch comprehensive stock data from Yahoo Finance including price, trends, and key metrics."
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if hist.empty:
                return "No data found for the given ticker symbol."
            info = stock.info
            current = hist["Close"].iloc[-1]
            month_start = hist["Close"].iloc[0]
            change_pct = (current - month_start) / month_start * 100
            high_30d = hist["High"].max()
            low_30d = hist["Low"].min()
            range_30d = high_30d - low_30d
            position_in_range = ((current - low_30d) / range_30d * 100) if range_30d > 0 else 50
            avg_volume = int(hist["Volume"].mean())

            lines = [
                f"Stock: {ticker}",
                f"Company: {info.get('shortName', 'N/A')}",
                f"Sector: {info.get('sector', 'N/A')}",
                f"Current Price: ${current:.2f}",
                f"30-Day Change: {change_pct:+.2f}%",
                f"30-Day High: ${high_30d:.2f}",
                f"30-Day Low: ${low_30d:.2f}",
                f"Position in 30-Day Range: {position_in_range:.0f}% (0%=at low, 100%=at high)",
                f"Avg Daily Volume (30d): {avg_volume:,}",
            ]

            week52_high = info.get("fiftyTwoWeekHigh")
            week52_low = info.get("fiftyTwoWeekLow")
            if week52_high and week52_low:
                lines.append(f"52-Week High: ${week52_high:.2f}")
                lines.append(f"52-Week Low: ${week52_low:.2f}")
                w52_range = week52_high - week52_low
                if w52_range > 0:
                    pos_52w = (current - week52_low) / w52_range * 100
                    lines.append(f"Position in 52-Week Range: {pos_52w:.0f}%")

            pe = info.get("trailingPE")
            fwd_pe = info.get("forwardPE")
            if pe:
                lines.append(f"P/E Ratio (Trailing): {pe:.1f}")
            if fwd_pe:
                lines.append(f"P/E Ratio (Forward): {fwd_pe:.1f}")

            mkt_cap = info.get("marketCap")
            if mkt_cap:
                if mkt_cap >= 1e12:
                    lines.append(f"Market Cap: ${mkt_cap/1e12:.2f}T")
                elif mkt_cap >= 1e9:
                    lines.append(f"Market Cap: ${mkt_cap/1e9:.2f}B")
                else:
                    lines.append(f"Market Cap: ${mkt_cap/1e6:.0f}M")

            div_yield = info.get("dividendYield")
            if div_yield and div_yield > 0:
                lines.append(f"Dividend Yield: {div_yield*100:.2f}%")

            target_mean = info.get("targetMeanPrice")
            if target_mean:
                upside = (target_mean - current) / current * 100
                lines.append(f"Analyst Mean Target: ${target_mean:.2f} ({upside:+.1f}% from current)")

            rec = info.get("recommendationKey")
            if rec:
                lines.append(f"Analyst Consensus: {rec.upper()}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching stock data: {str(e)}"


stock_search_tool = StockSearchTool()
yahoo_finance_tool = YahooFinanceTool()


@st.cache_resource
def get_agents(_llm):
    analyst = Agent(
        role="Senior Equity Research Analyst",
        goal=(
            "Conduct thorough research on the given stock. Gather: "
            "(1) latest news — earnings, guidance, analyst upgrades/downgrades, major business events, "
            "(2) financial data — current price, 30-day trend, highs, lows, volume, "
            "(3) valuation context — where the price sits relative to its recent range and "
            "whether it appears undervalued, fairly valued, or overvalued based on the data, "
            "(4) market sentiment — bullish, bearish, or neutral with evidence. "
            "Always cite specific numbers, dates, and sources."
        ),
        backstory=(
            "You are a senior equity research analyst with 15 years of experience. "
            "You take a data-driven approach — every claim is backed by a specific number or source. "
            "You evaluate stocks the way a portfolio manager would: price action, momentum, "
            "news catalysts, and relative valuation. You clearly separate confirmed facts "
            "from speculation. You focus only on what helps an investor decide to buy, hold, or sell."
        ),
        llm=_llm,
        tools=[stock_search_tool, yahoo_finance_tool],
    )
    writer = Agent(
        role="Investment Report Writer",
        goal=(
            "Write a clear, concise investment report that a non-expert investor can act on. "
            "The report must be simple to read, avoid jargon, and end with a clear verdict. "
            "Include: valuation assessment (undervalued / fairly valued / overvalued), "
            "BUY / HOLD / SELL recommendation, price target range, and key risks. "
            "Keep it focused — no fluff, no filler."
        ),
        backstory=(
            "You are an investment report writer known for making complex analysis simple. "
            "You write for everyday investors, not Wall Street insiders. Your reports are "
            "structured, scannable, and always end with a decisive verdict. You use bullet "
            "points, bold labels, and short paragraphs. You never hedge with vague language — "
            "if the data says buy, you say buy. If it says sell, you say sell."
        ),
        llm=_llm,
    )
    return analyst, writer

analyst_agent, writer_agent = get_agents(llm)

col_input, col_btn = st.columns([3, 1])
with col_input:
    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        max_chars=6,
        placeholder="e.g. AAPL, GOOGL, TSLA",
        label_visibility="collapsed",
    ).upper()
with col_btn:
    analyze_btn = st.button("Analyze Stock", type="primary", use_container_width=True)

if not analyze_btn:
    st.markdown("""
    <div class="how-it-works">
        <h3>How It Works</h3>
        <div class="step-row">
            <div class="step">
                <div class="num">1</div>
                <div class="desc">Enter a stock ticker symbol above</div>
            </div>
            <div class="step">
                <div class="num">2</div>
                <div class="desc">AI Analyst researches news &amp; financials</div>
            </div>
            <div class="step">
                <div class="num">3</div>
                <div class="desc">AI Writer crafts a detailed report</div>
            </div>
            <div class="step">
                <div class="num">4</div>
                <div class="desc">Download your analysis</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_tech, tab_usage, tab_limits = st.tabs(["Tech Stack", "How to Use", "Limitations"])

    with tab_tech:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="info-card">
                <h4>AI Framework</h4>
                <p>
                    <span class="tag">CrewAI</span> orchestrates two specialized AI agents that collaborate on each analysis.
                    The <b>Analyst Agent</b> researches news and financial data, then the <b>Writer Agent</b> synthesizes
                    everything into a readable report.
                </p>
            </div>
            <div class="info-card">
                <h4>Language Model</h4>
                <p>
                    <span class="tag">Llama 3.3 70B</span> via <span class="tag">Groq</span><br>
                    Meta's Llama 3.3 70B model running on Groq's ultra-fast LPU inference engine.
                    Delivers near-instant responses for complex reasoning tasks.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
            <div class="info-card">
                <h4>Data Sources</h4>
                <p>
                    <span class="tag">SerpAPI</span> Google News search for latest headlines and sentiment<br>
                    <span class="tag">Yahoo Finance</span> Real-time stock prices, 30-day history, highs, and lows
                </p>
            </div>
            <div class="info-card">
                <h4>Frontend & Deployment</h4>
                <p>
                    <span class="tag">Streamlit</span> <span class="tag">Python</span> <span class="tag">Streamlit Cloud</span><br>
                    Built with Streamlit for rapid prototyping. Deployed on Streamlit Community Cloud (free tier).
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab_usage:
        st.markdown("""
        <div class="info-card">
            <h4>Getting Started</h4>
            <ul>
                <li><b>Hosted keys available?</b> &mdash; Just enter a stock ticker (e.g. AAPL, TSLA, GOOGL) and click <b>Analyze Stock</b>. No setup needed.</li>
                <li><b>Using your own keys?</b> &mdash; Toggle "Use my own API keys" in the sidebar, paste your Groq and SerpAPI keys, then analyze.</li>
                <li>The analysis takes 15&ndash;30 seconds as two AI agents research and write your report.</li>
                <li>Once complete, read the report on-screen or click <b>Download Report</b> to save it as a text file.</li>
            </ul>
        </div>
        <div class="info-card">
            <h4>Getting API Keys (Free)</h4>
            <ul>
                <li><b>Groq</b> &mdash; Sign up at <a href="https://console.groq.com/keys" target="_blank">console.groq.com</a> and create an API key. Free tier available.</li>
                <li><b>SerpAPI</b> &mdash; Sign up at <a href="https://serpapi.com/" target="_blank">serpapi.com</a>. Free plan includes 100 searches/month.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab_limits:
        st.markdown("""
        <div class="info-card">
            <h4>Free Tier Limitations</h4>
            <div class="warn">
                This app runs entirely on free-tier services. You may occasionally hit rate limits &mdash; just wait a few seconds and try again.
            </div>
            <ul>
                <li><b>Groq Free Tier</b> &mdash; Limited to ~30 requests/minute and 12,000 tokens/minute (TPM). If you see a "rate limit" error, wait 10 seconds and retry. Heavy usage may require upgrading to Groq's Dev Tier.</li>
                <li><b>SerpAPI Free Tier</b> &mdash; 100 searches per month. Each analysis uses 1&ndash;2 searches.</li>
                <li><b>Hosted Keys</b> &mdash; Limited to a set number of analyses per session to protect shared quotas. Bring your own keys for unlimited use.</li>
                <li><b>Model</b> &mdash; Llama 3.3 70B is powerful but may occasionally produce inaccurate financial data or outdated information. Always verify important decisions with official sources.</li>
                <li><b>Streamlit Cloud</b> &mdash; App may sleep after inactivity. First load can take 30&ndash;60 seconds as it wakes up.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if analyze_btn:
    if not ticker:
        st.error("Please enter a stock ticker symbol.")
    elif not use_own_keys and not consume_hosted_quota(max_hosted_requests):
        st.error("Session limit reached. Toggle **Use my own API keys** in the sidebar.")
    else:
        snapshot = get_stock_snapshot(ticker)
        if snapshot:
            change_class = "positive" if snapshot["change_pct"] >= 0 else "negative"
            change_sign = "+" if snapshot["change_pct"] >= 0 else ""

            pe_html = ""
            if snapshot.get("pe"):
                pe_html = f'<div class="metric-card"><div class="label">P/E Ratio</div><div class="value">{snapshot["pe"]:.1f}</div>'
                if snapshot.get("fwd_pe"):
                    pe_html += f'<div class="sub">Fwd: {snapshot["fwd_pe"]:.1f}</div>'
                pe_html += '</div>'

            w52_html = ""
            if snapshot.get("w52_high") and snapshot.get("w52_low"):
                w52_html = f'<div class="metric-card"><div class="label">52-Week Range</div><div class="value" style="font-size:1rem">\\${snapshot["w52_low"]:.0f} - \\${snapshot["w52_high"]:.0f}</div></div>'

            target_html = ""
            if snapshot.get("analyst_target"):
                upside = (snapshot["analyst_target"] - snapshot["price"]) / snapshot["price"] * 100
                upside_class = "positive" if upside >= 0 else "negative"
                upside_sign = "+" if upside >= 0 else ""
                rec_label = (snapshot.get("recommendation") or "").upper()
                target_html = f'<div class="metric-card"><div class="label">Analyst Target</div><div class="value">\\${snapshot["analyst_target"]:.2f}</div><div class="sub {upside_class}">{upside_sign}{upside:.1f}% &bull; {rec_label}</div></div>'

            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="label">Company</div>
                    <div class="value" style="font-size:1.1rem">{snapshot["name"]}</div>
                    <div class="sub">{ticker}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Current Price</div>
                    <div class="value">\\${snapshot["price"]:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="label">30-Day Change</div>
                    <div class="value {change_class}">{change_sign}{snapshot["change_pct"]:.1f}%</div>
                </div>
                {pe_html}
                {w52_html}
                {target_html}
            </div>
            """, unsafe_allow_html=True)

        status = st.status(f"Analyzing **{ticker}**...", expanded=True)
        with status:
            try:
                st.markdown('<div class="agent-step"><span class="icon">1.</span><span class="text">Analyst: Researching news, earnings, and market sentiment...</span></div>', unsafe_allow_html=True)
                news_task = Task(
                    description=(
                        f"Research the latest news and market sentiment for {ticker}. Find: "
                        f"(1) most recent earnings results — did the company beat or miss estimates? "
                        f"Any guidance changes? "
                        f"(2) analyst actions — any recent upgrades, downgrades, or price target changes? "
                        f"What is the consensus rating? "
                        f"(3) major business events — new products, partnerships, acquisitions, "
                        f"lawsuits, leadership changes, insider buying/selling "
                        f"(4) sector trends — is the industry doing well or struggling? "
                        f"Rate the overall sentiment as BULLISH, BEARISH, or NEUTRAL with evidence."
                    ),
                    expected_output=(
                        "Structured findings: recent earnings summary (beat/miss/guidance), "
                        "analyst consensus and notable rating changes, key business developments, "
                        "sector outlook, and overall sentiment verdict (BULLISH/BEARISH/NEUTRAL)."
                    ),
                    agent=analyst_agent,
                )

                st.markdown('<div class="agent-step"><span class="icon">2.</span><span class="text">Analyst: Analyzing price action and valuation...</span></div>', unsafe_allow_html=True)
                price_task = Task(
                    description=(
                        f"Fetch financial data for {ticker} and perform a valuation assessment. Analyze: "
                        f"(1) current price vs 30-day high/low — is it near the top or bottom of its range? "
                        f"(2) 30-day price trend — uptrend, downtrend, or sideways? "
                        f"(3) momentum — is buying pressure increasing or decreasing? "
                        f"(4) support level (recent low where price bounced) and resistance level "
                        f"(recent high where price stalled) "
                        f"(5) valuation verdict — based on where the price sits in its range, "
                        f"the trend direction, and the news sentiment from the previous task, "
                        f"classify the stock as: UNDERVALUED (trading below fair value, potential upside), "
                        f"FAIRLY VALUED (price reflects current fundamentals), or "
                        f"OVERVALUED (price has run ahead of fundamentals, limited upside or downside risk). "
                        f"Explain your reasoning in 2-3 sentences."
                    ),
                    expected_output=(
                        "Financial summary: current price, 30-day change %, trend direction, "
                        "support and resistance levels, momentum assessment, and a clear "
                        "valuation verdict (UNDERVALUED / FAIRLY VALUED / OVERVALUED) with reasoning."
                    ),
                    agent=analyst_agent,
                )

                st.markdown('<div class="agent-step"><span class="icon">3.</span><span class="text">Writer: Composing investment report with verdict...</span></div>', unsafe_allow_html=True)
                report_task = Task(
                    description=(
                        f"Write a clean, easy-to-read investment report for {ticker}. "
                        f"Use the analyst's research and follow this EXACT structure:\n\n"
                        f"**Recommendation: BUY / HOLD / SELL** (pick one, bold it)\n"
                        f"**Valuation: UNDERVALUED / FAIRLY VALUED / OVERVALUED** (from analyst's assessment)\n"
                        f"**Price Target: $X - $Y** (estimated 3-6 month range)\n\n"
                        f"Then these sections:\n"
                        f"- **Why this rating** — 2-3 sentences explaining the recommendation\n"
                        f"- **What's happening** — 3-4 bullet points of the most important recent news, "
                        f"earnings, or analyst actions. Use specific numbers and dates.\n"
                        f"- **Price action** — Current price, 30-day trend, support/resistance levels, "
                        f"and where it sits in its range\n"
                        f"- **Reasons to be bullish** — 2-3 specific reasons the stock could go higher\n"
                        f"- **Risks to watch** — 2-3 specific risks that could hurt the stock\n"
                        f"- **The verdict** — End with a clear, decisive 2-3 sentence conclusion. "
                        f"Restate the recommendation, valuation, and price target. "
                        f"Tell the investor exactly what you would do.\n\n"
                        f"IMPORTANT: Keep it under 400 words. Use simple language — write for someone "
                        f"who reads financial news but is not a professional trader. Every sentence "
                        f"should help the reader make a decision. No filler."
                    ),
                    expected_output=(
                        "A structured report with: recommendation (BUY/HOLD/SELL), "
                        "valuation (undervalued/fairly valued/overvalued), price target range, "
                        "key news highlights, price action summary, bull case, risks, "
                        "and a decisive verdict. Simple language, under 400 words."
                    ),
                    agent=writer_agent,
                )

                crew = Crew(
                    agents=[analyst_agent, writer_agent],
                    tasks=[news_task, price_task, report_task],
                )
                result = crew.kickoff()

                status.update(label=f"Analysis complete for **{ticker}**", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Analysis failed", state="error", expanded=False)
                st.error(f"An error occurred: {str(e)}")
                st.stop()

        result_text = str(result).replace('$', r'\$')

        st.markdown(f"""
        <div class="report-container">
            <div class="report-header">
                <h2>Analysis Report: {ticker}</h2>
                <span class="report-badge">AI Generated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(result_text)

        st.markdown("")
        col_dl, col_spacer = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="Download Report",
                data=str(result),
                file_name=f"{ticker}_analysis.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with st.expander("Disclaimer & Limitations", expanded=False):
            st.markdown("""
            <div class="info-card" style="margin:0">
                <div class="warn" style="margin-bottom:0.8rem">
                    <b>Not Financial Advice</b> &mdash; This report is generated by AI for informational and educational purposes only.
                    It does not constitute financial advice, investment recommendations, or an offer to buy or sell securities.
                </div>
                <h4>Important Limitations</h4>
                <ul>
                    <li><b>AI-Generated Content</b> &mdash; This analysis is produced by Llama 3.3 70B, a large language model. It may contain inaccuracies, hallucinated data, or outdated information. Always verify key data points with official sources (SEC filings, company earnings reports, financial news).</li>
                    <li><b>Price Targets Are Estimates</b> &mdash; Any price targets or ranges mentioned are AI-generated projections, not guarantees. Stock prices are influenced by countless factors that no model can fully predict.</li>
                    <li><b>Data Freshness</b> &mdash; News is sourced from Google News via SerpAPI and may not include the very latest developments. Financial data comes from Yahoo Finance with possible delays.</li>
                    <li><b>No Personalization</b> &mdash; This report does not consider your financial situation, risk tolerance, investment goals, or tax implications. Consult a licensed financial advisor for personalized advice.</li>
                    <li><b>Past Performance</b> &mdash; Historical price data and trends do not guarantee future results.</li>
                </ul>
                <h4>About This App</h4>
                <ul>
                    <li><b>Model:</b> Meta Llama 3.3 70B Versatile via Groq LPU inference</li>
                    <li><b>Agents:</b> CrewAI multi-agent framework (Analyst + Writer)</li>
                    <li><b>Data:</b> SerpAPI (Google News), Yahoo Finance (yfinance)</li>
                    <li><b>Infrastructure:</b> Streamlit Cloud (free tier)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    Built by <a href="https://github.com/kinjalthehero">Kinjal Mistry</a> &nbsp;&bull;&nbsp;
    Powered by CrewAI, Groq &amp; Streamlit
</div>
""", unsafe_allow_html=True)
