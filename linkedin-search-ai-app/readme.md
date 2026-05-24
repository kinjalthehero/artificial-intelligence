# LinkedIn Job Search AI Agent

An AI-powered job search agent that scrapes LinkedIn for job postings, uses Google Gemini to score each job against your skills, saves relevant matches to a database, and emails you the top results.

## How It Works

1. **Scrape LinkedIn** — Playwright launches a headless Chromium browser, navigates to LinkedIn's public job search for a given keyword (e.g. "AI Engineer"), and extracts the title, company, location, and link from up to 20 job cards.
2. **Score with AI** — Each scraped job is sent to Google Gemini 2.5 Flash (via LangChain) along with your skills. The LLM returns a relevance verdict ("Relevant" or "Not Relevant") and a score out of 100.
3. **Save to database** — Every job and its score are stored in a local SQLite database (`jobs.db`). Duplicate links are skipped via a unique constraint.
4. **Display results** — The Streamlit UI shows only the relevant jobs with their details and a direct "Apply" link. A table of all saved jobs is displayed below.
5. **Email notification** — If any relevant jobs are found, a summary email is sent via Gmail SMTP with the job titles, companies, locations, and application links.

### Scheduled Mode

`scheduler.py` runs the full pipeline (scrape → score → save → email) every 6 hours as a background process, using a predefined skill set. This is meant to be run separately from the Streamlit app, e.g. in a Docker container or as a cron job.

## Architecture

```
User enters skills + keyword in Streamlit UI
        |
        v
+------------------+
|  scraper.py      |  Playwright (headless Chromium)
|  Scrape LinkedIn |──> Up to 20 job cards
+--------+---------+
         |
         v
+------------------+
|  agent.py        |  Google Gemini 2.5 Flash (LangChain)
|  Score each job  |──> "Relevant/Not Relevant" + score out of 100
+--------+---------+
         |
         v
+------------------+
|  database.py     |  SQLite
|  Save all jobs   |──> jobs.db (title, company, location, link, score)
+--------+---------+
         |
         v
+------------------+
|  mailer.py       |  Gmail SMTP
|  Email matches   |──> Summary of relevant jobs sent to your inbox
+------------------+
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI** | Streamlit |
| **LLM** | Google Gemini 2.5 Flash (via LangChain) |
| **Web Scraping** | Playwright (headless Chromium) |
| **Database** | SQLite |
| **Email** | Gmail SMTP (smtplib) |
| **Scheduling** | schedule (Python) |
| **Containerization** | Docker |

## Project Structure

```
linkedin-search-ai-app/
├── app.py            # Streamlit entry point — UI, orchestrates scrape → score → save → email
├── agent.py          # Gemini LLM integration — scores jobs against user skills
├── scraper.py        # Playwright LinkedIn scraper — extracts job cards
├── database.py       # SQLite operations — create table, insert, fetch
├── mailer.py         # Gmail SMTP email sender
├── scheduler.py      # Runs the full pipeline every 6 hours (headless, no UI)
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container setup with Playwright browser deps
└── .env.example      # Template for required environment variables
```

## Run Locally

```bash
cd linkedin-search-ai-app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
playwright install --with-deps
python3 -m streamlit run app.py
```

### Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in your keys:

```
GOOGLE_API_KEY=your_google_api_key_here
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=recipient_email@example.com
```

- **Google API Key** — Get a free key at [Google AI Studio](https://aistudio.google.com/apikey)
- **Gmail App Password** — Enable 2-Step Verification on your Google account, then create an [App Password](https://myaccount.google.com/apppasswords)

### Run with Docker

```bash
docker build -t linkedin-search-ai .
docker run -itd -p 8501:8501 --env-file .env --name linkedin-search linkedin-search-ai
```

The app will be available at `http://localhost:8501`.

### Run the Scheduler (headless)

```bash
python3 scheduler.py
```

This runs the scrape → score → save → email pipeline every 6 hours without the Streamlit UI. Edit the `SKILLS` variable in `scheduler.py` to set your skill set.

## Author

[Kinjal Mistry](https://github.com/kinjalthehero)
