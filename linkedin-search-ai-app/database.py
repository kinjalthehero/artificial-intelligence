import sqlite3
import pandas as pd

DB_NAME = "jobs.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        link TEXT UNIQUE,
        score TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_job(job):
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("""
        INSERT INTO jobs (title, company, location, link, score) 
        VALUES (?, ?, ?, ?, ?)
        """, (
            job['title'], 
            job['company'], 
            job['location'], 
            job['link'], 
            job['score']
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Job already exists: {job['link']}")
    finally:
        conn.close()

def fetch_jobs():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    return df