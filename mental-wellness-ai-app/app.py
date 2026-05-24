import os
import streamlit as st
from dotenv import load_dotenv
import threading

### langchain and gemini

from langchain_google_genai import (
    GoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

### voice support

import speech_recognition as sr
import pyttsx3

## load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

## streamlit UI

st.set_page_config(page_title="Mental Wellness Assistant", page_icon="🧠", layout="centered")

st.title("Mental Wellness Assistant")
st.markdown("Welcome to your personal mental wellness assistant! How can I help you today?")

st.warning("This is not a licensed therapist. Please consult a professional for serious mental health issues.")

### gemini model

llm = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=GOOGLE_API_KEY)

## embeddings and vector store

embeddings = GoogleGenerativeAIEmbeddings(google_api_key=GOOGLE_API_KEY, model="models/gemini-embedding-001")


vector_store = Chroma(
    collection_name="mental_wellness",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

## TTS engine

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Set speech rate

## session state for conversation history

if "messages" not in st.session_state:
    st.session_state.messages = []

if "speaking" not in st.session_state:
    st.session_state.speaking = False

if "speech_thread" not in st.session_state:
    st.session_state.speech_thread = None

## speach function

def _speak(text):

    try:
        st.session_state.speaking = True
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        st.error(f"Error occurred while speaking: {e}")
    finally:
        st.session_state.speaking = False

### start speaking

def speak_text(text):

    try:
        tts_engine.stop()
    except:
        pass

    speech_thread = threading.Thread(target=_speak, args=(text,))
    speech_thread.start()
    st.session_state.speech_thread = speech_thread


## stop speakiung

def stop_speaking():

    try:
        tts_engine.stop()
    except Exception as e:
        st.error(f"Error occurred while stopping speech: {e}")
    finally:
        st.session_state.speaking = False


## speech to text

def listen_to_user():

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("Listening... Please speak now.")
            recognizer.adjust_for_ambient_noise(source) 
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand what you said. Please try again.")
        return None


### display conversation history

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

### buttons for UI

col1, col2 = st.columns(2)

voice_input = None
with col1:
    if st.button("🎤 Speak"):
        voice_input = listen_to_user()
        if voice_input:
           st.success(f"You said: {voice_input}")


with col2:
    if st.button("⏹️ Stop Speaking"):
        stop_speaking()
        st.success("Stopped speaking.")

### text input for user

text_input = st.text_input("Type your message here...")

### final input

user_input = voice_input if voice_input else text_input

### main conversation logic

if user_input:

    ### show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    ### retriueve from long term story

    try:
        relevant_docs = vector_store.similarity_search(user_input, k=3)
        memory_context = "\n\n".join([doc.page_content for doc in relevant_docs])
    except Exception as e:
        print(f"Error retrieving from vector store: {e}")
        memory_context = ""

    #### prompt

    final_prompt = f"""
You are a compassionate mental wellness assistant. Use the following information to help answer the user's question:

Your responsibilities:
- Listen empathetically to the user's concerns.
- Respond calmly and supportively.
- Support emotional well-being and provide helpful advice.
- Never provide medical advice or attempt to diagnose conditions.
- Never provide harmful or triggering content.
- Do not share personal information or ask for sensitive details.
- Stick to general wellness advice and emotional support.
- Do not entertain queries that are inappropriate or harmful or not related to mental wellness.

If the user mentions:

- suicidal thoughts: Respond with empathy and encourage them to seek immediate help from a mental health professional or a trusted person in their life.
- self-harm: Express concern and suggest they talk to someone who can help, like a mental health professional.
- severe distress: Offer support and encourage them to reach out for help.
- sever depression: Provide empathetic responses and suggest they seek professional help.

Strongly encourage contacting:
- family members, friends, or mental health professionals for support.
- therapists, counselors, or support groups for ongoing help.
- helplines or crisis centers for immediate assistance.

Relevant Past Conversations:
{memory_context}

Current User Message:
{user_input}

Based on the above information, provide a supportive, calm and helpful response to the user's message.

"""
    
    ### Generate AI response
    response = llm.invoke(final_prompt)

    if hasattr(response, "content"):
        response_text = response.content
    else:
        response_text = str(response)

    ### crisis detection

    crisis_keywords = ["suicide", "self-harm", "severe distress", "severe depression"]

    lower_input = user_input.lower()

    if any(word in lower_input for word in crisis_keywords):

        response += """

**It seems like you might be going through a tough time. Please consider reaching out to a mental health professional, trusted friend, or family member for support. If you're in immediate danger, please contact emergency services or a crisis helpline. You're not alone, and there are people who care about you and want to help.**
"""

    ## save to long term memory

    try:
        vector_store.add_documents([
            Document(page_content=f"User: {user_input}\nAssistant: {response_text}",
                        metadata={
                            "type": "conversation"
                        }
                    )
        ])
    except Exception as e:
        st.error(f"Error saving to vector store: {e}")

    ### show AI response
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    ### speak AI response
    speak_text(response)

