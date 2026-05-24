import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.9,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# job from the LinkedIn scrapper and skills from the user input
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

    response = llm.invoke(prompt)

    return response.content
  
