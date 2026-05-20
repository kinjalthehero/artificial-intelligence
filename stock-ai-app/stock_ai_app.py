import os
import warnings
import streamlit as st

from config import consume_hosted_quota
from tools import get_stock_snapshot
from agents import create_llm, create_agents, run_analysis
from ui import (
    inject_css,
    render_hero,
    render_sidebar,
    render_metric_cards,
    render_report_header,
    render_disclaimer,
    render_footer,
    render_landing_page,
)

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Stock AI Analyst", page_icon="", layout="wide")
inject_css()

groq_key, serpapi_key, use_own_keys, max_hosted = render_sidebar()
render_hero()

if not groq_key or not serpapi_key:
    st.info(
        "Enter your API keys in the sidebar to get started, "
        "or use hosted keys if available."
    )
    st.stop()

os.environ["GROQ_API_KEY"] = groq_key
os.environ["SERPAPI_KEY"] = serpapi_key


@st.cache_resource
def _get_llm(_groq_key):
    return create_llm(_groq_key)


@st.cache_resource
def _get_agents(_llm):
    return create_agents(_llm)


llm = _get_llm(groq_key)
analyst_agent, writer_agent = _get_agents(llm)

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
    analyze_btn = st.button(
        "Analyze Stock", type="primary", use_container_width=True
    )

if not analyze_btn:
    render_landing_page()

if analyze_btn:
    if not ticker:
        st.error("Please enter a stock ticker symbol.")
    elif not use_own_keys and not consume_hosted_quota(max_hosted):
        st.error(
            "Session limit reached. Toggle **Use my own API keys** in the sidebar."
        )
    else:
        snapshot = get_stock_snapshot(ticker)
        if not snapshot:
            st.warning(
                f"**Could not fetch live price data for {ticker}** — Yahoo "
                f"Finance returned no data. The AI report will proceed without "
                f"live prices and may be less accurate. Please verify the ticker "
                f"symbol is correct."
            )
        if snapshot:
            render_metric_cards(ticker, snapshot)

        status = st.status(f"Analyzing **{ticker}**...", expanded=True)
        with status:
            try:
                st.markdown(
                    '<div class="agent-step"><span class="icon">1.</span>'
                    '<span class="text">Analyst: Researching news, earnings, '
                    "and market sentiment...</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="agent-step"><span class="icon">2.</span>'
                    '<span class="text">Analyst: Analyzing price action and '
                    "valuation...</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="agent-step"><span class="icon">3.</span>'
                    '<span class="text">Writer: Composing investment report '
                    "with verdict...</span></div>",
                    unsafe_allow_html=True,
                )

                result = run_analysis(
                    ticker, snapshot, analyst_agent, writer_agent
                )
                status.update(
                    label=f"Analysis complete for **{ticker}**",
                    state="complete",
                    expanded=False,
                )

            except Exception as e:
                status.update(
                    label="Analysis failed", state="error", expanded=False
                )
                err = str(e)
                if "rate_limit" in err.lower() or "ratelimit" in err.lower():
                    st.warning(
                        "**Groq Rate Limit Reached** — The free-tier AI model "
                        "has a limit of 12,000 tokens per minute. This happens "
                        "when too many requests are made in a short time.\n\n"
                        "**What to do:** Wait 15-30 seconds and click "
                        "**Analyze Stock** again. If this keeps happening, "
                        "toggle **Use my own API keys** in the sidebar and "
                        "enter your own free Groq key from "
                        "[console.groq.com](https://console.groq.com/keys)."
                    )
                elif (
                    "api_key" in err.lower()
                    or "authentication" in err.lower()
                    or "unauthorized" in err.lower()
                ):
                    st.error(
                        "**Invalid API Key** — The API key was rejected. "
                        "Please check that your Groq and SerpAPI keys are "
                        "correct in the sidebar."
                    )
                else:
                    st.error(
                        "**Analysis failed** — Something went wrong during "
                        f"the analysis. Please try again.\n\nDetails: {err}"
                    )
                st.stop()

        result_text = str(result).replace("$", r"\$")
        render_report_header(ticker, snapshot)
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

        render_disclaimer()

render_footer()
