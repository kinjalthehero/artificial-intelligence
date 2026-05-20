from crewai import Agent, Task, Crew, LLM
from tools import StockSearchTool, YahooFinanceTool


stock_search_tool = StockSearchTool()
yahoo_finance_tool = YahooFinanceTool()


def create_llm(groq_key: str) -> LLM:
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_key,
        temperature=0.7,
    )


def create_agents(llm: LLM):
    analyst = Agent(
        role="Senior Equity Research Analyst",
        goal=(
            "Conduct thorough research on the given stock. Gather: "
            "(1) latest news — earnings, guidance, analyst upgrades/downgrades, "
            "major business events, "
            "(2) financial data — current price, 30-day trend, highs, lows, volume, "
            "(3) valuation context — where the price sits relative to its recent "
            "range and whether it appears undervalued, fairly valued, or overvalued "
            "based on the data, "
            "(4) market sentiment — bullish, bearish, or neutral with evidence. "
            "Always cite specific numbers, dates, and sources."
        ),
        backstory=(
            "You are a senior equity research analyst with 15 years of experience. "
            "You take a data-driven approach — every claim is backed by a specific "
            "number or source. You evaluate stocks the way a portfolio manager "
            "would: price action, momentum, news catalysts, and relative valuation. "
            "You clearly separate confirmed facts from speculation. You focus only "
            "on what helps an investor decide to buy, hold, or sell."
        ),
        llm=llm,
        tools=[stock_search_tool, yahoo_finance_tool],
    )
    writer = Agent(
        role="Investment Report Writer",
        goal=(
            "Write a clear, concise investment report that a non-expert investor "
            "can act on. The report must be simple to read, avoid jargon, and end "
            "with a clear verdict. Include: valuation assessment (undervalued / "
            "fairly valued / overvalued), BUY / HOLD / SELL recommendation, price "
            "target range, and key risks. Keep it focused — no fluff, no filler."
        ),
        backstory=(
            "You are an investment report writer known for making complex analysis "
            "simple. You write for everyday investors, not Wall Street insiders. "
            "Your reports are structured, scannable, and always end with a decisive "
            "verdict. You use bullet points, bold labels, and short paragraphs. "
            "You never hedge with vague language — if the data says buy, you say "
            "buy. If it says sell, you say sell."
        ),
        llm=llm,
    )
    return analyst, writer


def build_price_context(ticker: str, snapshot: dict | None) -> str:
    if not snapshot:
        return ""
    parts = [f"LIVE DATA for {ticker} (from Yahoo Finance, fetched just now):"]
    parts.append(f"- Company: {snapshot['name']}")
    parts.append(f"- Current Price: ${snapshot['price']:.2f}")
    parts.append(f"- 30-Day Change: {snapshot['change_pct']:+.2f}%")
    parts.append(f"- 30-Day High: ${snapshot['high']:.2f}")
    parts.append(f"- 30-Day Low: ${snapshot['low']:.2f}")
    if snapshot.get("pe"):
        parts.append(f"- P/E Ratio (Trailing): {snapshot['pe']:.1f}")
    if snapshot.get("fwd_pe"):
        parts.append(f"- P/E Ratio (Forward): {snapshot['fwd_pe']:.1f}")
    if snapshot.get("w52_high") and snapshot.get("w52_low"):
        parts.append(f"- 52-Week High: ${snapshot['w52_high']:.2f}")
        parts.append(f"- 52-Week Low: ${snapshot['w52_low']:.2f}")
    if snapshot.get("analyst_target"):
        parts.append(
            f"- Analyst Mean Price Target: ${snapshot['analyst_target']:.2f}"
        )
    if snapshot.get("recommendation"):
        parts.append(
            f"- Analyst Consensus: {snapshot['recommendation'].upper()}"
        )
    return "\n".join(parts)


def _build_tasks(ticker, snapshot, price_context, analyst, writer):
    news_task = Task(
        description=(
            f"Research the latest news and market sentiment for {ticker}. Find: "
            f"(1) most recent earnings results — did the company beat or miss "
            f"estimates? Any guidance changes? "
            f"(2) analyst actions — any recent upgrades, downgrades, or price "
            f"target changes? What is the consensus rating? "
            f"(3) major business events — new products, partnerships, "
            f"acquisitions, lawsuits, leadership changes, insider buying/selling "
            f"(4) sector trends — is the industry doing well or struggling? "
            f"Rate the overall sentiment as BULLISH, BEARISH, or NEUTRAL with "
            f"evidence.\n\n{price_context}"
        ),
        expected_output=(
            "Structured findings: recent earnings summary (beat/miss/guidance), "
            "analyst consensus and notable rating changes, key business "
            "developments, sector outlook, and overall sentiment verdict "
            "(BULLISH/BEARISH/NEUTRAL)."
        ),
        agent=analyst,
    )

    if snapshot:
        price_desc = (
            f"Analyze the financial data for {ticker} and perform a valuation "
            f"assessment.\n\n{price_context}\n\n"
            f"Using the LIVE DATA above and your tools, analyze: "
            f"(1) current price vs 30-day high/low — is it near the top or "
            f"bottom of its range? "
            f"(2) 30-day price trend — uptrend, downtrend, or sideways? "
            f"(3) momentum — is buying pressure increasing or decreasing? "
            f"(4) support level (recent low where price bounced) and resistance "
            f"level (recent high where price stalled) "
            f"(5) valuation verdict — based on where the price sits in its "
            f"range, the P/E ratio, analyst targets, trend direction, and the "
            f"news sentiment, classify the stock as: UNDERVALUED (trading below "
            f"fair value, potential upside), FAIRLY VALUED (price reflects "
            f"current fundamentals), or OVERVALUED (price has run ahead of "
            f"fundamentals, limited upside or downside risk). Explain your "
            f"reasoning in 2-3 sentences. IMPORTANT: You MUST reference the "
            f"actual current price of ${snapshot['price']:.2f} in your analysis."
        )
    else:
        price_desc = (
            f"Fetch and analyze the financial data for {ticker}. Assess "
            f"valuation as UNDERVALUED, FAIRLY VALUED, or OVERVALUED."
        )

    price_task = Task(
        description=price_desc,
        expected_output=(
            "Financial summary: current price, 30-day change %, trend direction, "
            "support and resistance levels, momentum assessment, and a clear "
            "valuation verdict (UNDERVALUED / FAIRLY VALUED / OVERVALUED) with "
            "reasoning."
        ),
        agent=analyst,
    )

    price_line = (
        f"The current stock price is ${snapshot['price']:.2f}. "
        if snapshot
        else ""
    )

    if snapshot:
        report_desc = (
            f"Write a clean, easy-to-read investment report for {ticker}. "
            f"{price_line}"
            f"Use the analyst's research and the live data below.\n\n"
            f"{price_context}\n\n"
            f"Follow this EXACT structure:\n\n"
            f"**Recommendation: BUY / HOLD / SELL** (pick one, bold it)\n"
            f"**Valuation: UNDERVALUED / FAIRLY VALUED / OVERVALUED** "
            f"(from analyst's assessment)\n"
            f"**Price Target: $X - $Y** (estimated 3-6 month range — must be "
            f"realistic relative to the current price of "
            f"${snapshot['price']:.2f})\n\n"
            f"Then these sections:\n"
            f"- **Why this rating** — 2-3 sentences explaining the "
            f"recommendation\n"
            f"- **What's happening** — 3-4 bullet points of the most important "
            f"recent news, earnings, or analyst actions. Use specific numbers "
            f"and dates.\n"
            f"- **Price action** — Current price (${snapshot['price']:.2f}), "
            f"30-day trend, support/resistance levels, and where it sits in "
            f"its range\n"
        )
    else:
        report_desc = (
            f"Write a clean, easy-to-read investment report for {ticker}. "
            f"Follow this EXACT structure:\n\n"
            f"**Recommendation: BUY / HOLD / SELL** (pick one, bold it)\n"
            f"**Valuation: UNDERVALUED / FAIRLY VALUED / OVERVALUED** "
            f"(from analyst's assessment)\n"
            f"**Price Target: $X - $Y** (estimated 3-6 month range)\n\n"
            f"Then these sections:\n"
            f"- **Why this rating** — 2-3 sentences explaining the "
            f"recommendation\n"
            f"- **What's happening** — 3-4 bullet points of the most important "
            f"recent news, earnings, or analyst actions. Use specific numbers "
            f"and dates.\n"
            f"- **Price action** — Current price, 30-day trend, "
            f"support/resistance levels\n"
        )

    report_desc += (
        f"- **Reasons to be bullish** — 2-3 specific reasons the stock could "
        f"go higher\n"
        f"- **Risks to watch** — 2-3 specific risks that could hurt the stock\n"
        f"- **The verdict** — End with a clear, decisive 2-3 sentence "
        f"conclusion. Restate the recommendation, valuation, and price target. "
        f"Tell the investor exactly what you would do.\n\n"
        f"IMPORTANT: Keep it under 400 words. Use simple language. "
        f"The price target MUST be realistic — do not set a target below the "
        f"current price for a BUY recommendation or above it for a SELL "
        f"recommendation."
    )

    report_task = Task(
        description=report_desc,
        expected_output=(
            "A structured report with: recommendation (BUY/HOLD/SELL), "
            "valuation (undervalued/fairly valued/overvalued), price target "
            "range, key news highlights, price action summary, bull case, "
            "risks, and a decisive verdict. Simple language, under 400 words."
        ),
        agent=writer,
    )

    return [news_task, price_task, report_task]


def run_analysis(ticker: str, snapshot: dict | None, analyst, writer):
    price_context = build_price_context(ticker, snapshot)
    tasks = _build_tasks(ticker, snapshot, price_context, analyst, writer)
    crew = Crew(agents=[analyst, writer], tasks=tasks)
    return crew.kickoff()
