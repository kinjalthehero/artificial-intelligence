import streamlit as st


def render_landing_page():
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

    tab_tech, tab_usage, tab_limits = st.tabs(
        ["Tech Stack", "How to Use", "Limitations"]
    )

    with tab_tech:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="info-card">
                <h4>AI Framework</h4>
                <p>
                    <span class="tag">CrewAI</span> orchestrates two specialized
                    AI agents that collaborate on each analysis. The <b>Analyst
                    Agent</b> researches news and financial data, then the
                    <b>Writer Agent</b> synthesizes everything into a readable
                    report.
                </p>
            </div>
            <div class="info-card">
                <h4>Language Model</h4>
                <p>
                    <span class="tag">Llama 3.3 70B</span> via
                    <span class="tag">Groq</span><br>
                    Meta's Llama 3.3 70B model running on Groq's ultra-fast LPU
                    inference engine. Delivers near-instant responses for complex
                    reasoning tasks.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
            <div class="info-card">
                <h4>Data Sources</h4>
                <p>
                    <span class="tag">SerpAPI</span> Google News search for latest
                    headlines and sentiment<br>
                    <span class="tag">Yahoo Finance</span> Real-time stock prices,
                    30-day history, highs, and lows
                </p>
            </div>
            <div class="info-card">
                <h4>Frontend &amp; Deployment</h4>
                <p>
                    <span class="tag">Streamlit</span>
                    <span class="tag">Python</span>
                    <span class="tag">Streamlit Cloud</span><br>
                    Built with Streamlit for rapid prototyping. Deployed on
                    Streamlit Community Cloud (free tier).
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab_usage:
        st.markdown("""
        <div class="info-card">
            <h4>Getting Started</h4>
            <ul>
                <li><b>Hosted keys available?</b> &mdash; Just enter a stock ticker
                (e.g. AAPL, TSLA, GOOGL) and click <b>Analyze Stock</b>. No setup
                needed.</li>
                <li><b>Using your own keys?</b> &mdash; Toggle "Use my own API
                keys" in the sidebar, paste your Groq and SerpAPI keys, then
                analyze.</li>
                <li>The analysis takes 15&ndash;30 seconds as two AI agents
                research and write your report.</li>
                <li>Once complete, read the report on-screen or click
                <b>Download Report</b> to save it as a text file.</li>
            </ul>
        </div>
        <div class="info-card">
            <h4>Getting API Keys (Free)</h4>
            <ul>
                <li><b>Groq</b> &mdash; Sign up at
                <a href="https://console.groq.com/keys" target="_blank">
                console.groq.com</a> and create an API key. Free tier
                available.</li>
                <li><b>SerpAPI</b> &mdash; Sign up at
                <a href="https://serpapi.com/" target="_blank">serpapi.com</a>.
                Free plan includes 100 searches/month.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab_limits:
        st.markdown("""
        <div class="info-card">
            <h4>Free Tier Limitations</h4>
            <div class="warn">
                This app runs entirely on free-tier services. You may occasionally
                hit rate limits &mdash; just wait a few seconds and try again.
            </div>
            <ul>
                <li><b>Groq Free Tier</b> &mdash; Limited to ~30 requests/minute
                and 12,000 tokens/minute (TPM). If you see a "rate limit" error,
                wait 10 seconds and retry.</li>
                <li><b>SerpAPI Free Tier</b> &mdash; 100 searches per month. Each
                analysis uses 1&ndash;2 searches.</li>
                <li><b>Hosted Keys</b> &mdash; Limited to a set number of analyses
                per session to protect shared quotas. Bring your own keys for
                unlimited use.</li>
                <li><b>Model</b> &mdash; Llama 3.3 70B is powerful but may
                occasionally produce inaccurate financial data or outdated
                information. Always verify important decisions with official
                sources.</li>
                <li><b>Streamlit Cloud</b> &mdash; App may sleep after inactivity.
                First load can take 30&ndash;60 seconds as it wakes up.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
