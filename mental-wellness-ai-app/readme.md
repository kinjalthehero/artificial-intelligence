# Mental Wellness AI Assistant

A conversational mental wellness chatbot with voice support, long-term memory, and crisis detection. Built with Streamlit, Google Gemini, and ChromaDB.

## How It Works

- **Text & Voice Input** — Type a message or use the microphone button for speech-to-text (Google Speech Recognition)
- **AI Responses** — Google Gemini 2.5 Flash generates empathetic, supportive responses via LangChain
- **Long-Term Memory** — Conversations are stored in a ChromaDB vector store and retrieved via similarity search (RAG), so the assistant remembers context across messages
- **Text-to-Speech** — Responses are spoken aloud using pyttsx3 (runs in a background thread to avoid blocking the UI)
- **Crisis Detection** — If the user mentions keywords like "suicide" or "self-harm", the assistant appends helpline and professional support guidance

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI** | Streamlit |
| **LLM** | Google Gemini 2.5 Flash (via LangChain) |
| **Embeddings** | Gemini Embedding 001 |
| **Vector Store** | ChromaDB (local persistence) |
| **Speech-to-Text** | SpeechRecognition (Google) |
| **Text-to-Speech** | pyttsx3 |

## Run Locally

```bash
cd mental-wellness-ai-app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

### API Key Setup

1. Copy `.env.example` to `.env`
2. Add your Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

### System Dependencies

PyAudio requires PortAudio. On macOS:

```bash
brew install portaudio
```

## Limitations

- **Voice features require local runtime** — Microphone access and TTS do not work in cloud deployments
- **Ephemeral memory** — ChromaDB persists to `./chroma_db` locally; this is lost on cloud platforms with ephemeral filesystems
- **Not a substitute for professional help** — This is an AI demo for educational purposes only

## Author

[Kinjal Mistry](https://github.com/kinjalthehero)
