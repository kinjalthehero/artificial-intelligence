import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

def _create_llm(model):
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.9,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

def analyze_job(job, skills):
    prompt = f"""
    Analyze this job description and identify the most relevant openings:

    User Skills: {skills}

    Job:
    Title: {job['title']}
    Company: {job['company']}
    Location: {job['location']}

    Give ONLY:
    Relevant or Not Relevant
    Score out of 100
    """

    for model in MODELS:
        try:
            llm = _create_llm(model)
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                continue
            raise

    raise RuntimeError("All Gemini models exceeded their rate limits. Please try again later.")
  
