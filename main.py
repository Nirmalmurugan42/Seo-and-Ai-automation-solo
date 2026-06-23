"""
The SEO Intelligence Agent — orchestrator.

Run:  python -m core.main

Pipeline per keyword (matches the 12-step workflow in your PDF):
  1. load target keywords (from your SEO team's CSV)         [data_loader]
  2. live Google search -> our rank + competitor URLs        [serp_client]
  3. scrape our page + competitor pages                      [scraper]
  4. factual gap analysis (TF-IDF, word count, headings)     [analyzer]
  5. LLM -> optimized title/meta/outline/FAQ/brief           [llm_client]
  6. collect into a report row
  ... then write Excel + HTML reports                        [reporter]
"""
from __future__ import annotations

import time
from urllib.parse import urljoin

from . import config
from .analyzer import analyse
from .data_loader import load_focus_keywords
from .llm_client import generate_recommendations
from .reporter import write_excel, write_html
from .scraper import scrape
from .serp_client import get_serp_client


def _own_page_url(target_page: str) -> str:
    base = f"https://{config.OWN_DOMAIN}"
    if not target_page or target_page.lower() in ("homepage", "home"):
        return base + "/"
    return urljoin(base + "/", target_page.lstrip("/"))


def run() -> None:
    print("=" * 70)
    print(f"  SEO Intelligence Agent — {config.OWN_BRAND} ({config.OWN_DOMAIN})")
    print(f"  LLM provider: {config.LLM_PROVIDER}")
    print("=" * 70)

    keywords = load_focus_keywords(limit=config.MAX_KEYWORDS)
    print(f"Loaded {len(keywords)} priority keywords.\n")

    serp = get_serp_client()
    rows: list[dict] = []

    for i, kw in enumerate(keywords, 1):
        print(f"[{i}/{len(keywords)}] {kw.keyword}")

        # 2. live SERP
        try:
            serp_data = serp.analyse_serp(kw.keyword)
        except Exception as exc:  # noqa: BLE001
            print(f"     ! SERP failed: {exc}")
            continue

        kw.our_current_rank = serp_data["own_rank"]
        kw.competitor_urls = serp_data["competitor_urls"]
        print(f"     our rank: {kw.our_current_rank or 'not in top ' + str(config.SERP_NUM)}"
              f"  | competitors: {len(kw.competitor_urls)}")

        # 3. scrape
        our_url = _own_page_url(kw.target_page)
        our_page = scrape(our_url)
        comp_pages = [scrape(u) for u in kw.competitor_urls]
        ok = sum(c.ok for c in comp_pages)
        print(f"     scraped our page ({'ok' if our_page.ok else 'FAILED'}) "
              f"+ {ok}/{len(comp_pages)} competitor pages")

        # 4. gap analysis
        gap = analyse(kw.keyword, our_page, comp_pages)

        # 5. LLM recommendations
        try:
            rec = generate_recommendations(
                gap, brand=config.OWN_BRAND,
                target_page=kw.target_page, intent=kw.intent,
            )
            print(f"     recommendations generated ({rec.get('_provider')})")
        except Exception as exc:  # noqa: BLE001
            print(f"     ! LLM failed: {exc}")
            rec = {}

        rows.append({
            "group": kw.group,
            "keyword": kw.keyword,
            "volume": kw.volume,
            "difficulty": kw.difficulty,
            "intent": kw.intent,
            "target_page": kw.target_page,
            "top_company": kw.top_company,
            "our_rank": kw.our_current_rank,
            "word_gap": gap.word_count_gap,
            "kw_in_title": gap.keyword_in_title,
            "kw_in_h1": gap.keyword_in_h1,
            "missing_terms": gap.missing_terms,
            "recommendation": rec,
        })

        time.sleep(1)  # be polite to SerpAPI / target servers

    if not rows:
        print("\nNo rows produced — check your API keys / network.")
        return

    xlsx = write_excel(rows)
    html_path = write_html(rows)
    print("\nDone.")
    print(f"  Excel: {xlsx}")
    print(f"  HTML : {html_path}")


if __name__ == "__main__":
    run()
