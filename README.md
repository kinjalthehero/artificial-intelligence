# Stock AI App (Streamlit + CrewAI)

A multi-agent stock analysis app using:
- `CrewAI` for agent orchestration
- `Groq` for LLM inference
- `SerpAPI` for stock news
- `yfinance` for market data

## Run locally

```zsh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run stock_ai_app.py
```

### Local secrets setup

1. Create `.streamlit/secrets.toml`.
2. Copy values from `.streamlit/secrets.toml.example`.
3. Fill your real keys.

## Deploy from GitHub (recommended: Streamlit Community Cloud)

1. Push this project to your GitHub repo.
2. Keep `runtime.txt` in the repo (`python-3.11`) so Streamlit does not use Python 3.14.
3. In Streamlit Community Cloud, create a new app from your repo.
4. Set `Main file path` to `stock_ai_app.py`.
5. In **App settings -> Secrets**, add:

```toml
GROQ_API_KEY = "..."
SERPAPI_KEY = "..."
APP_PASSWORD = "optional"
MAX_REQUESTS_PER_SESSION = 5
```

6. Deploy.

## Important key-safety notes

- Do **not** hardcode API keys in code.
- Do **not** commit `.streamlit/secrets.toml`.
- Public apps that use your shared free-tier keys can be abused.
- For safer usage, set `APP_PASSWORD` and keep the app for invited users.
- If you want fully public usage, ask users to toggle **Use my own API keys**.

## Key behavior in this app

- If hosted secrets exist, users can run with owner keys.
- Users can switch to their own keys in the sidebar.
- Owner-key usage has a simple per-session cap via `MAX_REQUESTS_PER_SESSION`.

