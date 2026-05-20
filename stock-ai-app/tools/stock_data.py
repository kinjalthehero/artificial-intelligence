from typing import Type
import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class YahooFinanceInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol to fetch data for.")


def get_stock_snapshot(ticker_symbol: str):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info or {}

        hist = None
        for period in ("1mo", "5d", "3mo"):
            try:
                h = stock.history(period=period, repair=True)
                if not h.empty:
                    hist = h
                    break
            except Exception:
                continue

        if hist is None or hist.empty:
            current = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("previousClose")
            )
            if not current:
                return None
            return {
                "price": current,
                "change_pct": 0.0,
                "high": current,
                "low": current,
                "volume": info.get("volume", 0),
                "name": info.get("shortName", ticker_symbol),
                "pe": info.get("trailingPE"),
                "fwd_pe": info.get("forwardPE"),
                "w52_high": info.get("fiftyTwoWeekHigh"),
                "w52_low": info.get("fiftyTwoWeekLow"),
                "analyst_target": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationKey"),
            }

        current = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[0]
        change_pct = (current - prev) / prev * 100 if prev != 0 else 0.0
        return {
            "price": current,
            "change_pct": change_pct,
            "high": hist["High"].max(),
            "low": hist["Low"].min(),
            "volume": int(hist["Volume"].iloc[-1]),
            "name": info.get("shortName", ticker_symbol),
            "pe": info.get("trailingPE"),
            "fwd_pe": info.get("forwardPE"),
            "w52_high": info.get("fiftyTwoWeekHigh"),
            "w52_low": info.get("fiftyTwoWeekLow"),
            "analyst_target": info.get("targetMeanPrice"),
            "recommendation": info.get("recommendationKey"),
        }
    except Exception:
        return None


class YahooFinanceTool(BaseTool):
    name: str = "YahooFinanceData"
    description: str = (
        "Fetch comprehensive stock data from Yahoo Finance "
        "including price, trends, and key metrics."
    )
    args_schema: Type[BaseModel] = YahooFinanceInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            hist = None
            for period in ("1mo", "5d", "3mo"):
                try:
                    h = stock.history(period=period, repair=True)
                    if not h.empty:
                        hist = h
                        break
                except Exception:
                    continue

            if hist is None or hist.empty:
                current = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                    or info.get("previousClose")
                )
                if not current:
                    return "No data found for the given ticker symbol."
                lines = [
                    f"Stock: {ticker}",
                    f"Company: {info.get('shortName', 'N/A')}",
                    f"Sector: {info.get('sector', 'N/A')}",
                    f"Current Price: ${current:.2f}",
                    "Note: Historical price data temporarily unavailable; "
                    "using last known price.",
                ]
            else:
                current = hist["Close"].iloc[-1]
                month_start = hist["Close"].iloc[0]
                change_pct = (
                    (current - month_start) / month_start * 100
                    if month_start != 0
                    else 0.0
                )
                high_30d = hist["High"].max()
                low_30d = hist["Low"].min()
                range_30d = high_30d - low_30d
                position_in_range = (
                    ((current - low_30d) / range_30d * 100)
                    if range_30d > 0
                    else 50
                )
                avg_volume = int(hist["Volume"].mean())

                lines = [
                    f"Stock: {ticker}",
                    f"Company: {info.get('shortName', 'N/A')}",
                    f"Sector: {info.get('sector', 'N/A')}",
                    f"Current Price: ${current:.2f}",
                    f"30-Day Change: {change_pct:+.2f}%",
                    f"30-Day High: ${high_30d:.2f}",
                    f"30-Day Low: ${low_30d:.2f}",
                    f"Position in 30-Day Range: {position_in_range:.0f}% "
                    f"(0%=at low, 100%=at high)",
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
                    lines.append(f"Market Cap: ${mkt_cap / 1e12:.2f}T")
                elif mkt_cap >= 1e9:
                    lines.append(f"Market Cap: ${mkt_cap / 1e9:.2f}B")
                else:
                    lines.append(f"Market Cap: ${mkt_cap / 1e6:.0f}M")

            div_yield = info.get("dividendYield")
            if div_yield and div_yield > 0:
                lines.append(f"Dividend Yield: {div_yield * 100:.2f}%")

            target_mean = info.get("targetMeanPrice")
            if target_mean:
                upside = (target_mean - current) / current * 100
                lines.append(
                    f"Analyst Mean Target: ${target_mean:.2f} "
                    f"({upside:+.1f}% from current)"
                )

            rec = info.get("recommendationKey")
            if rec:
                lines.append(f"Analyst Consensus: {rec.upper()}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching stock data: {str(e)}"
