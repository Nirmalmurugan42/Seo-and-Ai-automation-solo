"""
SerpAPI client.

Two jobs:
  1. discover_competitors(keyword) -> the URLs Google currently ranks top-N for.
  2. find_own_rank(keyword)        -> where OUR domain currently sits (or None).

SerpAPI runs the actual Google search for us so we don't get blocked.
Docs: https://serpapi.com/search-api
"""
from __future__ import annotations

import requests

from . import config


class SerpClient:
    BASE = "https://serpapi.com/search.json"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.SERPAPI_KEY
        if not self.api_key:
            raise RuntimeError(
                "SERPAPI_KEY is not set. Add it to your .env file "
                "(get a free key at https://serpapi.com)."
            )

    def _search(self, keyword: str) -> list[dict]:
        params = {
            "engine": "google",
            "q": keyword,
            "location": config.SERP_LOCATION,
            "gl": config.SERP_GL,
            "hl": config.SERP_HL,
            "num": config.SERP_NUM,
            "api_key": self.api_key,
        }
        resp = requests.get(self.BASE, params=params, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic_results", []) or []

    def analyse_serp(self, keyword: str) -> dict:
        """
        Return both the competitor URLs and our own current rank in one call,
        so we only spend one SerpAPI credit per keyword.
        """
        results = self._search(keyword)
        own_rank = None
        competitors: list[str] = []

        for r in results:
            link = r.get("link", "")
            position = r.get("position")
            if not link:
                continue
            if config.OWN_DOMAIN in link:
                if own_rank is None:
                    own_rank = position
            else:
                competitors.append(link)

        return {
            "keyword": keyword,
            "own_rank": own_rank,
            "competitor_urls": competitors[: config.COMPETITORS_PER_KEYWORD],
            "all_results": [
                {"position": r.get("position"), "link": r.get("link"),
                 "title": r.get("title")}
                for r in results
            ],
        }


# Offline stub so the rest of the pipeline can be developed/tested without
# burning SerpAPI credits. Used automatically when SERPAPI_KEY is missing
# AND OFFLINE_DEMO=1 is set.
class SerpClientStub:
    def analyse_serp(self, keyword: str) -> dict:
        sample = {
            "managed cyber security services": [
                "https://www.tesserent.com/managed-cyber-security-services/",
                "https://www.cybercx.com.au/managed-security-services/",
                "https://www.cyberwardens.com.au/",
            ],
        }
        urls = sample.get(keyword, [
            "https://www.tesserent.com/",
            "https://www.cybercx.com.au/",
        ])
        return {
            "keyword": keyword,
            "own_rank": None,
            "competitor_urls": urls[: config.COMPETITORS_PER_KEYWORD],
            "all_results": [],
        }


def get_serp_client():
    import os
    if not config.SERPAPI_KEY and os.getenv("OFFLINE_DEMO") == "1":
        print("  [serp] no key + OFFLINE_DEMO=1 -> using stub data")
        return SerpClientStub()
    return SerpClient()
