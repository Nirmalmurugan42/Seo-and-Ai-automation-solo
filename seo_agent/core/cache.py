import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent.parent / "seo_cache.db"


def init_cache():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS page_cache (
        url TEXT PRIMARY KEY,
        title TEXT,
        meta_description TEXT,
        h1 TEXT,
        h2 TEXT,
        h3 TEXT,
        word_count INTEGER,
        internal_links INTEGER,
        external_links INTEGER,
        text TEXT,
        cached_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_cached_page(url, max_age_hours=24):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM page_cache WHERE url = ?", (url,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    cached_at = datetime.fromisoformat(row[10])
    if datetime.now() - cached_at > timedelta(hours=max_age_hours):
        return None

    return row


def save_cached_page(page):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO page_cache (
        url, title, meta_description, h1, h2, h3,
        word_count, internal_links, external_links, text, cached_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        page.url,
        page.title,
        page.meta_description,
        "|||".join(page.h1),
        "|||".join(page.h2),
        "|||".join(page.h3),
        page.word_count,
        page.internal_links,
        page.external_links,
        page.text,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()