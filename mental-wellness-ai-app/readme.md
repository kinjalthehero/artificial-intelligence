# Mental Wellness AI Assistant

A conversational mental wellness chatbot with voice support, long-term memory, and crisis detection. Built with Streamlit, Google Gemini, and ChromaDB.

## How It Works

When you send a message, the app follows this flow:

1. **Retrieve context** — Your input is embedded and compared against past conversations stored in a ChromaDB vector store. The most relevant prior exchanges are pulled in as context, giving the assistant long-term memory across messages.
2. **Generate a response** — The retrieved context and your current message are combined into a prompt and sent to Google Gemini 2.5 Flash (via LangChain). The LLM produces an empathetic, supportive response grounded in both the current conversation and relevant history.
3. **Display the answer** — The response is rendered in the Streamlit chat interface and the conversation is saved back to the vector store for future retrieval.
4. **Read it aloud** — The response is spoken using pyttsx3 text-to-speech in a background thread, so the UI stays responsive while the assistant talks.

### Additional Features

- **Voice Input** — Use the microphone button for speech-to-text (Google Speech Recognition) instead of typing
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
