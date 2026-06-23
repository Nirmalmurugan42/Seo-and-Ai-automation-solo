import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).resolve().parent.parent / "seo_history.db"


def _rank_to_number(rank):
    if not rank or str(rank).lower() == "not ranked":
        return None
    try:
        return int(rank)
    except ValueError:
        return None


def get_ranking_trends():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT keyword, rank, checked_at
    FROM ranking_history
    ORDER BY keyword, checked_at
    """)

    rows = cur.fetchall()
    conn.close()

    grouped = defaultdict(list)

    for keyword, rank, checked_at in rows:
        grouped[keyword].append({
            "rank": rank,
            "checked_at": checked_at,
        })

    trends = []

    for keyword, history in grouped.items():
        if len(history) < 2:
            continue

        previous = history[-2]
        current = history[-1]

        prev_rank_num = _rank_to_number(previous["rank"])
        curr_rank_num = _rank_to_number(current["rank"])

        if prev_rank_num is None and curr_rank_num is None:
            trend = "No Change"
        elif prev_rank_num is None and curr_rank_num is not None:
            trend = "Improved"
        elif prev_rank_num is not None and curr_rank_num is None:
            trend = "Dropped"
        elif curr_rank_num < prev_rank_num:
            trend = "Improved"
        elif curr_rank_num > prev_rank_num:
            trend = "Dropped"
        else:
            trend = "No Change"

        trends.append({
            "keyword": keyword,
            "previous_rank": previous["rank"],
            "current_rank": current["rank"],
            "trend": trend,
            "previous_checked_at": previous["checked_at"],
            "current_checked_at": current["checked_at"],
        })

    return trends