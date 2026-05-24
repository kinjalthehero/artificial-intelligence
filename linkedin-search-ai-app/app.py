import streamlit as st

from scraper import scrape_linkedin_jobs
from agent import analyze_job
from database import create_table, insert_job, fetch_jobs
from mailer import send_email

create_table()
st.title("AI Job Agent")
skills = st.text_area("Enter Skills")
keyword = st.text_input("Job Keyword", "AI Engineer")

if st.button("Find Jobs"):
    # Scrape LinkedIn for jobs matching the keyword
    jobs = scrape_linkedin_jobs(keyword)

    relevant_jobs = []

    for job in jobs:
        try:
            result = analyze_job(job, skills)
        except Exception as e:
            st.warning(f"Rate limit reached — scored {len(relevant_jobs)} of {len(jobs)} jobs before quota ran out.")
            break
        job["score"] = result
        insert_job(job)
        if "Relevant" in result:
            relevant_jobs.append(job)

    st.success(f"Found {len(relevant_jobs)} Relevant Jobs")

    for job in relevant_jobs:
        st.subheader(job["title"])
        st.write(job["company"])
        st.write(job["location"])
        st.write(job["score"])
        st.link_button("Apply", job["link"])

    if relevant_jobs:
        try:
            send_email(relevant_jobs)
            st.success("Email Sent")
        except Exception as e:
            st.warning(f"Could not send email: {e}")

st.divider()
st.subheader("Saved Jobs")
df = fetch_jobs()
st.dataframe(df)