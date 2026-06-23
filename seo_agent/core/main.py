"""
The SEO Intelligence Agent — orchestrator.

Run:
    python -m core.main
"""

from __future__ import annotations

import time
from urllib.parse import urljoin
import datetime as dt
from pathlib import Path

from . import config
from .analyzer import analyse
from .data_loader import load_focus_keywords
from .llm_client import generate_recommendations
from .reporter import write_excel, write_html, write_pdf
from .scraper import scrape
from .serp_client import get_serp_client
from pathlib import Path
from .pdf_report import write_pdf
from .database import init_db, save_ranking
from .trends import get_ranking_trends

def _own_page_url(target_page: str) -> str:

    base = f"https://{config.OWN_DOMAIN}"

    if not target_page or target_page.lower() in ("homepage", "home"):
        return base + "/"

    return urljoin(base + "/", target_page.lstrip("/"))


def _calculate_rankability_score(volume, difficulty, word_gap, current_rank):
    score = 0

    try:
        volume = int(volume or 0)
    except ValueError:
        volume = 0

    try:
        difficulty = int(difficulty or 0)
    except ValueError:
        difficulty = 0

    word_gap = abs(word_gap or 0)

    if volume > 0:
        score += min(int(volume / 10), 40)

    if difficulty > 0:
        score += max(0, 30 - difficulty)

    if word_gap > 100:
        score += 20

    if not current_rank:
        score += 10

    if score >= 80:
        priority = "High"
    elif score >= 60:
        priority = "Medium"
    else:
        priority = "Low"

    return score, priority


def run() -> None:
    print("=" * 70)
    print(f"SEO Intelligence Agent — {config.OWN_BRAND} ({config.OWN_DOMAIN})")
    print(f"LLM provider: {config.LLM_PROVIDER}")
    print("=" * 70)

    keywords = load_focus_keywords(limit=config.MAX_KEYWORDS)
    print(f"Loaded {len(keywords)} priority keywords.\n")

    serp = get_serp_client()
    rows: list[dict] = []
    init_db()

    for i, kw in enumerate(keywords, 1):
        print(f"[{i}/{len(keywords)}] {kw.keyword}")

        try:
            serp_data = serp.analyse_serp(kw.keyword)
        except Exception as exc:
            print(f"     ! SERP failed: {exc}")
            continue

        kw.our_current_rank = serp_data.get("own_rank")
        save_ranking(kw.keyword, kw.our_current_rank, kw.volume, kw.difficulty)
        kw.competitor_urls = serp_data.get("competitor_urls", [])

        rank_text = kw.our_current_rank or f"not in top {config.SERP_NUM}"
        print(f"     our rank: {rank_text} | competitors: {len(kw.competitor_urls)}")

        our_url = _own_page_url(kw.target_page)
        our_page = scrape(our_url)

        comp_pages = [scrape(url) for url in kw.competitor_urls]
        ok_competitors = sum(page.ok for page in comp_pages)

        print(
            f"     scraped our page ({'ok' if our_page.ok else 'FAILED'}) "
            f"+ {ok_competitors}/{len(comp_pages)} competitor pages"
        )

        gap = analyse(kw.keyword, our_page, comp_pages)

        score, priority = _calculate_rankability_score(
            kw.volume,
            kw.difficulty,
            gap.word_count_gap,
            kw.our_current_rank,
        )

        try:
            rec = generate_recommendations(
                gap=gap,
                brand=config.OWN_BRAND,
                target_page=kw.target_page,
                intent=kw.intent,
            )

            if rec.get("_error"):
                print(f"     ! LLM JSON warning: {rec.get('_error')}")
            else:
                print(f"     recommendations generated ({rec.get('_provider')})")

        except Exception as exc:
            print(f"     ! LLM failed: {exc}")
            rec = {}

        rows.append(
    {
        "group": kw.group,
        "keyword": kw.keyword,
        "volume": kw.volume,
        "difficulty": kw.difficulty,
        "intent": kw.intent,
        "target_page": kw.target_page,
        "top_company": kw.top_company,
        "our_rank": kw.our_current_rank,
        "jypra_word_count": gap.our_word_count,
        "competitor_avg_word_count": gap.competitor_avg_word_count,
        "word_gap": gap.word_count_gap,
        "jypra_h2_count": gap.our_h2_count,
        "competitor_avg_h2_count": gap.competitor_avg_h2_count,
        "kw_in_title": gap.keyword_in_title,
        "kw_in_h1": gap.keyword_in_h1,
        "rankability_score": score,
        "priority": priority,
        "missing_terms": gap.missing_terms,
        "recommendation": rec,
    }
)

        time.sleep(1)

    if not rows:
        print("\nNo rows produced. Check API keys, CSV files, or network.")
        return

    xlsx = write_excel(rows)
    trend_data = get_ranking_trends()
    html_path = write_html(
    rows=rows,
    trend_data=trend_data,
    ) 
    pdf_path = config.REPORTS_DIR / f"seo_report_{dt.date.today().isoformat()}.pdf"
    write_pdf(rows, pdf_path)


    print("\nDone.")
    print(f"  Excel: {xlsx}")
    print(f"  HTML : {html_path}")
    print(f"  PDF  : {pdf_path}")


if __name__ == "__main__":
    run()