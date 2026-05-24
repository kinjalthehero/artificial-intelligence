# AI Projects

A collection of AI/ML projects.

## Projects

### [stock-ai-app](stock-ai-app/)

A multi-agent stock analysis app using:
- `CrewAI` for agent orchestration
- `Groq` for LLM inference
- `SerpAPI` for stock news
- `yfinance` for market data

### [mental-wellness-ai-app](mental-wellness-ai-app/)

A conversational mental wellness chatbot with voice support and long-term memory using:
- `Google Gemini` for LLM inference (via LangChain)
- `ChromaDB` for conversation memory (RAG)
- `SpeechRecognition` + `pyttsx3` for voice I/O

#### Run locally

```zsh
cd "stock-ai-app"
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run stock_ai_app.py
```

#### Local secrets setup

1. Create `stock-ai-app/.streamlit/secrets.toml`.
2. Copy values from `stock-ai-app/.streamlit/secrets.toml.example`.
3. Fill your real keys.

#### Deploy from GitHub (recommended: Streamlit Community Cloud)

1. Push this project to your GitHub repo.
2. Keep `runtime.txt` (`python-3.11`) and `.python-version` (`3.11`) in the repo.
3. Keep `packages.txt` in the repo to install system dependencies (`rustc`, `cargo`, `build-essential`) needed when Streamlit builds `tiktoken` from source.
4. In Streamlit Community Cloud, create a new app from your repo.
5. Set `Main file path` to `stock-ai-app/stock_ai_app.py`.
6. In **App settings -> Secrets**, add:

```toml
GROQ_API_KEY = "..."
SERPAPI_KEY = "..."
APP_PASSWORD = "optional"
MAX_REQUESTS_PER_SESSION = 5
```

7. Deploy.

#### Important key-safety notes

- Do **not** hardcode API keys in code.
- Do **not** commit `.streamlit/secrets.toml`.
- For safer usage, set `APP_PASSWORD` and keep the app for invited users.
- If you want fully public usage, ask users to toggle **Use my own API keys**.
