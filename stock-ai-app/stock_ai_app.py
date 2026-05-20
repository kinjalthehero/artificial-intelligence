### create stock analysis app using streamlit and crew framework

"""
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt
$ python3 -m streamlit run stock_ai_app.py

1. Define tools for agents - News from SerpAPI (Google News engine). Finance data from Yahoo Finance.
2. Create agents using these tools
3. Assign task to each of these agents 
4. Work with them together using CrewAI 
"""


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
    # Recommended: newer official SerpAPI client package.
    from serpapi import Client as SerpApiClient
except ImportError:
    SerpApiClient = None

LegacyGoogleSearch: Any = None
try:
    # Legacy fallback from google-search-results package.
    from serpapi import GoogleSearch as LegacyGoogleSearch
except ImportError:
    LegacyGoogleSearch = None

# ignore warnings for cleaner output
warnings.filterwarnings("ignore")

# Streamlit page configuration
st.set_page_config(page_title="Stock Analysis App using AI", page_icon="📈", layout="wide")
st.title("📈 Stock Analysis App using AI")
st.markdown("Multi agent system powered by CrewAI and Groq")


def get_config_value(name: str) -> str:
    "Return config from Streamlit secrets first, then environment."
    secret_value = st.secrets.get(name)
    if secret_value:
        return str(secret_value)
    return os.getenv(name, "")


def consume_hosted_quota(max_requests: int) -> bool:
    "Simple per-session limit to protect shared free-tier keys from abuse."
    used = st.session_state.get("hosted_requests_used", 0)
    if used >= max_requests:
        return False
    st.session_state["hosted_requests_used"] = used + 1
    return True

### sidebar for user input
hosted_groq_key = get_config_value("GROQ_API_KEY")
hosted_serpapi_key = get_config_value("SERPAPI_KEY")
app_password = get_config_value("APP_PASSWORD")
max_hosted_requests = int(get_config_value("MAX_REQUESTS_PER_SESSION") or 5)

with st.sidebar:
    st.header("Access")
    if app_password:
        access_password = st.text_input("App Password", type="password")
        if access_password != app_password:
            st.warning("Enter the app password to continue.")
            st.stop()

    st.header("API Keys Configuration")
    hosted_keys_ready = bool(hosted_groq_key and hosted_serpapi_key)
    use_own_keys = st.toggle("Use my own API keys", value=not hosted_keys_ready)

    if use_own_keys:
        groq_key = st.text_input("Enter your Groq API Key", type="password")
        serpapi_key = st.text_input("Enter your SerpAPI Key", type="password")
    else:
        groq_key = hosted_groq_key
        serpapi_key = hosted_serpapi_key
        used = st.session_state.get("hosted_requests_used", 0)
        st.caption(f"Hosted usage this session: {used}/{max_hosted_requests}")

    st.markdown("[Get your Groq API Key](https://console.groq.com/keys)")
    st.markdown("[Get your SerpAPI Key](https://serpapi.com/)")

    st.markdown("---")
    st.info("Use your own keys for personal usage, or hosted keys if enabled by the app owner.")

if not groq_key or not serpapi_key:
    st.warning("Groq and SerpAPI keys are required. Add your own keys or configure hosted keys in secrets.")
    st.stop()

## setup environment variables for CrewAI
os.environ["GROQ_API_KEY"] = groq_key
os.environ["SERPAPI_KEY"] = serpapi_key

### initialize LLM
## default groq model is llama3-8b
# cache the LLM initialization to avoid re-initializing on every run which can be time consuming
@st.cache_resource
def get_llm(_groq_key):
    return LLM(model="groq/llama-3.3-70b-versatile", api_key=_groq_key, temperature=0.7)

llm = get_llm(groq_key)


### Query for Google API to search news
class StockSearchInput(BaseModel):
    # Field - Pydantic wat to validate
    # ... - required field. creating the model without query will raise a validation error
    query: str = Field(..., description="The stock ticker or company name to search for.")

class YahooFinanceInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol to fetch data for.")

# Define tools - News from Google API
class StockSearchTool(BaseTool):
    name: str = "StockNewsSearch"
    description: str = "Search for the latest news and information about a stock using SerpAPI."
    # args_schema defines the expected input format for the tool.
    # It uses Pydantic models to validate and structure the input data.
    # In this case, StockSearchInput expects a single field 'query' which is a string representing the stock ticker or company name to search for.
    args_schema: Type[BaseModel] = StockSearchInput

    # the _run method is where the actual logic of the tool is implemented.
    # It takes the input query, performs a search using SerpAPI, and returns the top 3 news results related to the stock ticker or company name.
    # _run can't be called from outside, it can be called only from internal methods
    def _run(self, query: str) -> str:
        "search for news related to the stock ticker or company name using SerpAPI and return the top 3 results"
        try:
            # Using Serp API to search for news related to the stock ticker or company name
            params = {
                "engine": "google",
                "q": query, 
                "api_key": os.getenv("SERPAPI_KEY"),
                "tbm": "nws",
                "num": 3
            }
            if SerpApiClient:
                client = SerpApiClient(api_key=params["api_key"])
                results = client.search({"engine": "google_news", "q": query, "num": 3})
            elif LegacyGoogleSearch:
                search = LegacyGoogleSearch(params)
                results = search.get_dict()
            else:
                return "SerpAPI client is not installed. Install `serpapi` (recommended) or `google-search-results` (legacy fallback)."

            news = results.get("news_results", results.get("organic_results", []))

            if not news:
                return "No news found for the given query."
            
            output = []

            for item in news[:3]:  # Limit to top 3 results
                title = item.get("title", "")
                snippet = item.get("snippet", item.get("description", ""))
                output.append(f"Title: {title}: {snippet[:100]}")

            return "\n\n".join(output)
    
        except Exception as e:
            return f"Error fetching news: {str(e)}"
        
# Define tools - Finance info from Yahoo finance
class YahooFinanceTool(BaseTool):
    name: str = "YahooFinanceData"
    description: str = "Fetch stock data from Yahoo Finance using yfinance library."
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str) -> str:
        "fetch stock data for the given ticker symbol using yfinance"
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")

            if hist.empty:
                return "No data found for the given ticker symbol."
            
            latest = hist.tail(5)
            current = latest["Close"].iloc[-1]
            change = (latest["Close"].iloc[-1] - latest["Close"].iloc[0]) / latest["Close"].iloc[0] * 100

            return f"""Stock: {ticker}\nPrice: ${current:.2f}\nChange (1 month): {change:.2f}%\nHigh: ${latest["High"].max():.2f}\nLow: ${latest["Low"].min():.2f}"""
        
        except Exception as e:
            return f"Error fetching stock data: {str(e)}"
        
## initializing tools
stock_search_tool = StockSearchTool()
yahoo_finance_tool = YahooFinanceTool()

## create agents

@st.cache_resource
def get_agents(_llm):
    analyst = Agent(
        role="Stock Analyst Agent",
        goal="Analyze the stock based on the latest news and financial data, and provide insights and recommendations.",
        backstory="You are a stock analyst with expertise in financial markets and news analysis. Your task is to analyze the stock based on the latest news and financial data, and provide insights and recommendations.",
        llm=_llm,
        tools=[stock_search_tool, yahoo_finance_tool]
    )

    writer = Agent(
        role="Stock Report Writer Agent",
        goal="Write a comprehensive stock analysis report based on the insights provided by the analyst agent.",
        backstory="You are a skilled writer with expertise in financial writing. Your task is to write a comprehensive stock analysis report based on the insights provided by the analyst agent.",
        llm=_llm
    )

    return analyst, writer
analyst_agent, writer_agent = get_agents(llm)


## interface for user input
col1, col2 = st.columns([2, 1])

with col1:
    ticker = st.text_input("Enter Stock Ticker Symbol", value="AAPL", max_chars=6).upper()

with col2:
    analyze_btn = st.button("Analyze Stock", type="primary", use_container_width=True)

if analyze_btn:
    if not ticker:
        st.error("Please enter a stock ticker symbol to analyze.")
    elif not use_own_keys and not consume_hosted_quota(max_hosted_requests):
        st.error("Hosted free-tier limit reached for this session. Please use your own API keys.")
    else:
        with st.spinner(f"Analyzing stock {ticker}..."):
            try:

                ### Assigning task to each agent
                news_task = Task(
                    description=f"Search for the latest news about {ticker} and provide insights.",
                    expected_output="Insights based on the latest news about the stock.",
                    agent = analyst_agent
                )

                price_task = Task(
                    description=f"Fetch the latest financial data for {ticker} and provide insights.",
                    expected_output="Insights based on the latest financial data of the stock.",
                    agent = analyst_agent
                )

                report_task = Task(
                    description=f"Write a comprehensive stock analysis report for {ticker} based on the insights from the news and financial data.Keep under 300 words",
                    expected_output="A comprehensive stock analysis report.",
                    agent = writer_agent
                )

                crew = Crew(
                    agents = [analyst_agent, writer_agent],
                    tasks = [news_task, price_task, report_task]
                )

                result = crew.kickoff()

                ## convert to string for display
                result_text = str(result).replace('$', r'\$')

                st.success("Stock analysis completed!")

                st.markdown("-----")
                st.markdown(f"### Stock Analysis Report for {ticker}")
                st.markdown(result_text)
                st.markdown("-----")

                ## download option for the report
                st.download_button(
                    label="Download Report",
                    data=str(result),
                    file_name=f"{ticker}_stock_analysis_report.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"An error occurred during stock analysis: {str(e)}")