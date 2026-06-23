import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "seo_history.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ranking_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        rank TEXT,
        volume INTEGER,
        difficulty INTEGER,
        checked_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_ranking(keyword, rank, volume, difficulty):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO ranking_history (keyword, rank, volume, difficulty, checked_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        keyword,
        str(rank) if rank else "Not ranked",
        int(volume or 0),
        int(difficulty or 0),
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()