"""
Gap analysis engine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer

from .scraper import PageContent


NOISE_TERMS = {
    "field",
    "hidden",
    "viewing",
    "form",
    "channel",
    "input",
    "submit",
    "button",
    "cookie",
    "privacy",
    "subscribe",
    "contact",
}


@dataclass
class GapReport:
    keyword: str
    our_url: str
    our_word_count: int
    competitor_avg_word_count: int
    word_count_gap: int
    keyword_in_title: bool
    keyword_in_h1: bool
    keyword_density_pct: float
    our_h2_count: int
    competitor_avg_h2_count: int
    missing_terms: list[str] = field(default_factory=list)
    competitor_titles: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _contains(haystack: str, needle: str) -> bool:
    return needle.lower() in (haystack or "").lower()


def _density(text: str, keyword: str) -> float:
    words = text.lower().split()

    if not words:
        return 0.0

    keyword_lower = keyword.lower()
    count = len(re.findall(re.escape(keyword_lower), text.lower()))

    return round(100.0 * count * len(keyword_lower.split()) / len(words), 2)


def analyse(
    keyword: str,
    our_page: PageContent,
    competitor_pages: list[PageContent],
    top_n_missing: int = 15,
) -> GapReport:
    comp_ok = [
        page for page in competitor_pages
        if page.ok and page.word_count > 50
    ]

    comp_avg_wc = (
        int(sum(page.word_count for page in comp_ok) / len(comp_ok))
        if comp_ok else 0
    )

    comp_avg_h2 = (
        int(sum(len(page.h2) for page in comp_ok) / len(comp_ok))
        if comp_ok else 0
    )

    raw_gap = comp_avg_wc - our_page.word_count

    report = GapReport(
        keyword=keyword,
        our_url=our_page.url,
        our_word_count=our_page.word_count,
        competitor_avg_word_count=comp_avg_wc,
        word_count_gap=raw_gap,
        keyword_in_title=_contains(our_page.title, keyword),
        keyword_in_h1=any(_contains(h, keyword) for h in our_page.h1),
        keyword_density_pct=_density(our_page.text, keyword),
        our_h2_count=len(our_page.h2),
        competitor_avg_h2_count=comp_avg_h2,
        competitor_titles=[page.title for page in comp_ok if page.title],
    )

    docs = [page.text for page in comp_ok]

    if docs:
        try:
            vec = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                max_features=400,
                min_df=1,
            )

            matrix = vec.fit_transform(docs)
            scores = matrix.mean(axis=0).A1
            terms = vec.get_feature_names_out()
            ranked = sorted(zip(terms, scores), key=lambda item: item[1], reverse=True)

            our_text = (our_page.text or "").lower()

            missing = [
                term for term, _ in ranked
                if term not in our_text
                and len(term) > 3
                and term.lower().strip() not in NOISE_TERMS
            ]

            report.missing_terms = missing[:top_n_missing]

        except ValueError:
            report.missing_terms = []

    if not report.keyword_in_title:
        report.notes.append(f'Add the exact phrase "{keyword}" to the page title.')

    if not report.keyword_in_h1:
        report.notes.append(f'Add "{keyword}" to the H1 heading.')

    if report.word_count_gap > 150:
        report.notes.append(
            f"Page is ~{report.word_count_gap} words thinner than competitors "
            f"(you: {report.our_word_count}, them: {comp_avg_wc}). Expand it."
        )

    if report.word_count_gap < -150:
        report.notes.append(
            f"Page has ~{abs(report.word_count_gap)} more words than competitors. "
            "Review content quality and make sure it is focused."
        )

    if report.our_h2_count < comp_avg_h2:
        report.notes.append(
            f"Add more sub-sections: competitors average {comp_avg_h2} H2 "
            f"headings, you have {report.our_h2_count}."
        )

    if report.keyword_density_pct < 0.3:
        report.notes.append(
            "Target keyword barely appears in the body — work it in naturally."
        )

    return report