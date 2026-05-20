import streamlit as st

CSS = """
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
    .metric-card .label {
        font-size: 0.75rem; color: #6b7280;
        text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
    }
    .metric-card .value {
        font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin-top: 2px;
    }
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
    .report-header h2 {
        margin: 0; font-size: 1.4rem; font-weight: 700; color: #1a1a2e;
    }
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
    .step { flex: 1; text-align: center; padding: 0.5rem; }
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
        margin: 0 0 0.6rem 0; font-size: 0.95rem;
        font-weight: 600; color: #1a1a2e;
    }
    .info-card p, .info-card li {
        font-size: 0.85rem; color: #4b5563; line-height: 1.6; margin: 0;
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
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)
