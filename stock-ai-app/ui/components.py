import streamlit as st
from config import get_config_value


def render_hero():
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


def render_sidebar():
    hosted_groq_key = get_config_value("GROQ_API_KEY")
    hosted_serpapi_key = get_config_value("SERPAPI_KEY")
    app_password = get_config_value("APP_PASSWORD")
    max_hosted = int(get_config_value("MAX_REQUESTS_PER_SESSION") or 5)

    with st.sidebar:
        st.markdown("## Settings")

        if app_password:
            access_password = st.text_input("App Password", type="password")
            if access_password != app_password:
                st.warning("Enter the app password to continue.")
                st.stop()

        st.markdown("## API Keys")
        hosted_keys_ready = bool(hosted_groq_key and hosted_serpapi_key)
        use_own_keys = st.toggle(
            "Use my own API keys", value=not hosted_keys_ready
        )

        if use_own_keys:
            groq_key = st.text_input(
                "Groq API Key", type="password", placeholder="gsk_..."
            )
            serpapi_key = st.text_input(
                "SerpAPI Key", type="password", placeholder="..."
            )
        else:
            groq_key = hosted_groq_key
            serpapi_key = hosted_serpapi_key
            used = st.session_state.get("hosted_requests_used", 0)
            remaining = max_hosted - used
            st.caption(
                f"Analyses remaining: **{remaining}** / {max_hosted}"
            )

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
            "Two AI agents collaborate to research and write stock analysis "
            "reports. The <b>Analyst</b> gathers news and financial data, then "
            "the <b>Writer</b> produces a comprehensive report."
            "</span>",
            unsafe_allow_html=True,
        )

    return groq_key, serpapi_key, use_own_keys, max_hosted


def render_metric_cards(ticker: str, snapshot: dict):
    change_class = "positive" if snapshot["change_pct"] >= 0 else "negative"
    change_sign = "+" if snapshot["change_pct"] >= 0 else ""

    pe_html = ""
    if snapshot.get("pe"):
        pe_html = (
            '<div class="metric-card">'
            '<div class="label">P/E Ratio</div>'
            f'<div class="value">{snapshot["pe"]:.1f}</div>'
        )
        if snapshot.get("fwd_pe"):
            pe_html += f'<div class="sub">Fwd: {snapshot["fwd_pe"]:.1f}</div>'
        pe_html += "</div>"

    w52_html = ""
    if snapshot.get("w52_high") and snapshot.get("w52_low"):
        w52_html = (
            '<div class="metric-card">'
            '<div class="label">52-Week Range</div>'
            f'<div class="value" style="font-size:1rem">'
            f'${snapshot["w52_low"]:.0f} - ${snapshot["w52_high"]:.0f}'
            "</div></div>"
        )

    target_html = ""
    if snapshot.get("analyst_target"):
        upside = (
            (snapshot["analyst_target"] - snapshot["price"])
            / snapshot["price"]
            * 100
        )
        upside_class = "positive" if upside >= 0 else "negative"
        upside_sign = "+" if upside >= 0 else ""
        rec_label = (snapshot.get("recommendation") or "").upper()
        target_html = (
            '<div class="metric-card">'
            '<div class="label">Analyst Target</div>'
            f'<div class="value">${snapshot["analyst_target"]:.2f}</div>'
            f'<div class="sub {upside_class}">'
            f"{upside_sign}{upside:.1f}% &bull; {rec_label}</div></div>"
        )

    has_history = (
        snapshot.get("change_pct") != 0.0
        or snapshot.get("high") != snapshot.get("low")
    )
    if has_history:
        change_val = f'{change_sign}{snapshot["change_pct"]:.1f}%'
    else:
        change_val = "N/A"
        change_class = ""

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="label">Company</div>
            <div class="value" style="font-size:1.1rem">{snapshot["name"]}</div>
            <div class="sub">{ticker}</div>
        </div>
        <div class="metric-card">
            <div class="label">Current Price</div>
            <div class="value">${snapshot["price"]:.2f}</div>
        </div>
        <div class="metric-card">
            <div class="label">30-Day Change</div>
            <div class="value {change_class}">{change_val}</div>
        </div>
        {pe_html}
        {w52_html}
        {target_html}
    </div>
    """, unsafe_allow_html=True)


def render_report_header(ticker: str, snapshot: dict | None):
    if snapshot:
        has_history = (
            snapshot.get("change_pct") != 0.0
            or snapshot.get("high") != snapshot.get("low")
        )
        if has_history:
            cls = "positive" if snapshot["change_pct"] >= 0 else "negative"
            sign = "+" if snapshot["change_pct"] >= 0 else ""
            change_html = (
                f"<span style='font-size:1.6rem; font-weight:700;' "
                f"class='{cls}'>{sign}{snapshot['change_pct']:.1f}%</span>"
            )
        else:
            change_html = (
                "<span style='font-size:1.1rem; font-weight:600; "
                "color:#6b7280;'>N/A</span>"
            )

        w52 = ""
        if snapshot.get("w52_high") and snapshot.get("w52_low"):
            w52 = (
                "<div><span style='font-size:0.75rem; color:#6b7280; "
                "text-transform:uppercase; font-weight:600;'>52-Week Range"
                "</span><br><span style='font-size:1.1rem; font-weight:600; "
                f"color:#374151;'>${snapshot['w52_low']:.0f} - "
                f"${snapshot['w52_high']:.0f}</span></div>"
            )

        pe = ""
        if snapshot.get("pe"):
            pe = (
                "<div><span style='font-size:0.75rem; color:#6b7280; "
                "text-transform:uppercase; font-weight:600;'>P/E</span><br>"
                "<span style='font-size:1.1rem; font-weight:600; "
                f"color:#374151;'>{snapshot['pe']:.1f}</span></div>"
            )

        target = ""
        if snapshot.get("analyst_target"):
            target = (
                "<div><span style='font-size:0.75rem; color:#6b7280; "
                "text-transform:uppercase; font-weight:600;'>Analyst Target"
                "</span><br><span style='font-size:1.1rem; font-weight:600; "
                f"color:#374151;'>${snapshot['analyst_target']:.2f}"
                "</span></div>"
            )

        st.markdown(f"""
        <div class="report-container">
            <div class="report-header">
                <h2>Analysis Report: {ticker}</h2>
                <span class="report-badge">AI Generated</span>
            </div>
            <div style="display:flex; gap:24px; flex-wrap:wrap; margin-top:0.5rem;">
                <div>
                    <span style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; font-weight:600;">Live Price</span><br>
                    <span style="font-size:1.6rem; font-weight:700; color:#1a1a2e;">${snapshot['price']:.2f}</span>
                </div>
                <div>
                    <span style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; font-weight:600;">30-Day</span><br>
                    {change_html}
                </div>
                {w52}
                {pe}
                {target}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="report-container">
            <div class="report-header">
                <h2>Analysis Report: {ticker}</h2>
                <span class="report-badge">AI Generated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_disclaimer():
    with st.expander("Disclaimer & Limitations", expanded=False):
        st.markdown("""
        <div class="info-card" style="margin:0">
            <div class="warn" style="margin-bottom:0.8rem">
                <b>Not Financial Advice</b> &mdash; This report is generated by AI
                for informational and educational purposes only. It does not
                constitute financial advice, investment recommendations, or an
                offer to buy or sell securities.
            </div>
            <h4>Important Limitations</h4>
            <ul>
                <li><b>AI-Generated Content</b> &mdash; This analysis is produced
                by Llama 3.3 70B, a large language model. It may contain
                inaccuracies, hallucinated data, or outdated information. Always
                verify key data points with official sources (SEC filings, company
                earnings reports, financial news).</li>
                <li><b>Price Targets Are Estimates</b> &mdash; Any price targets or
                ranges mentioned are AI-generated projections, not guarantees.</li>
                <li><b>Data Freshness</b> &mdash; News is sourced from Google News
                via SerpAPI and may not include the very latest developments.
                Financial data comes from Yahoo Finance with possible delays.</li>
                <li><b>No Personalization</b> &mdash; This report does not consider
                your financial situation, risk tolerance, investment goals, or tax
                implications. Consult a licensed financial advisor for personalized
                advice.</li>
                <li><b>Past Performance</b> &mdash; Historical price data and trends
                do not guarantee future results.</li>
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


def render_footer():
    st.markdown("""
    <div class="footer">
        Built by <a href="https://github.com/kinjalthehero">Kinjal Mistry</a>
        &nbsp;&bull;&nbsp; Powered by CrewAI, Groq &amp; Streamlit
    </div>
    """, unsafe_allow_html=True)
