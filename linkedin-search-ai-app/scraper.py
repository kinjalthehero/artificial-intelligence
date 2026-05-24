# This script uses Playwright to scrape LinkedIn job postings for a given keyword.
# Plawright is a powerful web scraping library that can handle dynamic content and JavaScript rendering, making it ideal for scraping LinkedIn.
# It collects the job title, company name, location, and link to the job posting.
# The results are returned as a list of dictionaries.
from playwright.sync_api import sync_playwright

#  Scrape LinkedIn job postings for a given keyword
def scrape_linkedin_jobs(keyword="AI Engineer"):

    jobs = []

    # Use Playwright to scrape LinkedIn job postings
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
        page.goto(url)
        page.wait_for_timeout(5000)
        cards = page.query_selector_all(".base-card")

        for card in cards[:20]:
            try:
                title = card.query_selector(".base-search-card__title").inner_text()
                company = card.query_selector(".base-search-card__subtitle").inner_text()
                location = card.query_selector(".job-search-card__location").inner_text()
                link = card.query_selector("a").get_attribute("href")
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link
                })
            except:
                continue

        browser.close()

    return jobs