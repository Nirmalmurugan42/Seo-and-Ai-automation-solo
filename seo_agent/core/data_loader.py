"""
Loads the keyword data your SEO team produced (the CSV exports from
Google Keyword Planner / Semrush) into clean Python objects.

These CSVs already contain the "Semrush-type" metrics (volume, difficulty),
so the agent does NOT need a paid Semrush API to run. Semrush stays optional
(see README -> "Where Semrush fits").
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from . import config


@dataclass
class KeywordTarget:
    group: str                    # Quick Win / Local SEO / Commercial / ...
    keyword: str
    volume: int | None            # monthly search volume
    difficulty: int | None        # 0-100 keyword difficulty
    intent: str                   # Informational / Commercial / Transactional
    target_page: str              # which page on our site this should hit
    top_company: str              # who currently ranks #1-ish
    top_position: int | None
    # filled in later by the agent:
    our_current_rank: int | None = None
    competitor_urls: list[str] = field(default_factory=list)


def _to_int(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    if not value or not any(c.isdigit() for c in value):
        return None
    digits = "".join(c for c in value if c.isdigit())
    return int(digits) if digits else None


def _read_rows(path: Path) -> list[list[str]]:
    """Read a CSV tolerantly (handles the BOM / odd bytes in the exports)."""
    with open(path, "r", encoding="utf-8", errors="ignore", newline="") as fh:
        return list(csv.reader(fh))


def load_focus_keywords(
    path: Path | None = None,
    groups: list[str] | None = None,
    limit: int | None = None,
) -> list[KeywordTarget]:
    """
    Parse 'SEO_competitors_keywords_Keyword_Focus_List_.csv'.

    The file has a title row, a header row, and group-divider rows
    ("Quick Wins", "Local SEO", ...) sprinkled between the data rows.
    We detect the header by the 'Sl. No' cell and treat anything with a
    real keyword in column 2 as a data row.
    """
    path = path or (config.DATA_DIR / "SEO_competitors_keywords_Keyword_Focus_List_.csv")
    groups = groups or config.TARGET_GROUPS
    rows = _read_rows(path)

    keywords: list[KeywordTarget] = []
    header_seen = False

    for row in rows:
        if not row or len(row) < 3:
            continue
        first = (row[0] or "").strip()

        if first.lower().startswith("sl. no"):
            header_seen = True
            continue
        if not header_seen:
            continue  # still in the title block

        group = (row[1] or "").strip()
        keyword = (row[2] or "").strip()

        # skip divider rows like "Quick Wins,,,,," and blank rows
        if not keyword or not group:
            continue

        kt = KeywordTarget(
            group=group,
            keyword=keyword,
            volume=_to_int(row[3]) if len(row) > 3 else None,
            difficulty=_to_int(row[4]) if len(row) > 4 else None,
            intent=(row[6].strip() if len(row) > 6 else ""),
            target_page=(row[7].strip() if len(row) > 7 else ""),
            top_company=(row[8].strip() if len(row) > 8 else ""),
            top_position=_to_int(row[9]) if len(row) > 9 else None,
        )

        # group filter (case/space tolerant)
        if groups and not any(g.lower() in kt.group.lower() for g in groups):
            continue

        keywords.append(kt)

    # priority sort: lower difficulty first within the requested group order
    def sort_key(k: KeywordTarget):
        try:
            g_idx = next(i for i, g in enumerate(groups) if g.lower() in k.group.lower())
        except StopIteration:
            g_idx = len(groups)
        return (g_idx, k.difficulty if k.difficulty is not None else 999)

    keywords.sort(key=sort_key)
    if limit:
        keywords = keywords[:limit]
    return keywords


if __name__ == "__main__":
    kws = load_focus_keywords(limit=15)
    print(f"Loaded {len(kws)} keyword targets:\n")
    for k in kws:
        print(
            f"  [{k.group:14s}] {k.keyword:42s} vol={k.volume}  "
            f"diff={k.difficulty}  -> {k.target_page}  (top: {k.top_company})"
        )
