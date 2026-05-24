import schedule
import time

from scraper import scrape_linkedin_jobs
from agent import analyze_job
from mailer import send_email
from database import insert_job

SKILLS = """
AZURE
Kubernetes
LangChain
Python
Machine Learning
GenAI
Docker
"""

# This function will run the AI job agent every 6 hours to scrape LinkedIn,
# analyze jobs, save relevant ones to the database, and send an email with top matches.
def run_agent():
    print("Running AI job agent...")

    jobs = scrape_linkedin_jobs("AI Engineer")

    relevant_jobs = []
    for job in jobs:
        result = analyze_job(job, SKILLS)
        job["score"] = result

        if "Relevant" in result:
            relevant_jobs.append(job)
            insert_job(job)

    if relevant_jobs:
        send_email(relevant_jobs)
        print("Email sent with top matching jobs!")

schedule.every(6).hours.do(run_agent)

while True:
    schedule.run_pending()
    time.sleep(60)