"""
Page scraper + on-page content extractor with caching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from . import config
from .cache import init_cache, get_cached_page, save_cached_page


@dataclass
class PageContent:
    url: str
    ok: bool = False
    error: str = ""
    title: str = ""
    meta_description: str = ""
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    h3: list[str] = field(default_factory=list)
    word_count: int = 0
    internal_links: int = 0
    external_links: int = 0
    text: str = ""


def _clean(text: str) -> str:
    return " ".join(text.split())


def scrape(url: str) -> PageContent:
    init_cache()

    cached = get_cached_page(url)
    if cached:
        return PageContent(
            url=cached[0],
            ok=True,
            title=cached[1],
            meta_description=cached[2],
            h1=cached[3].split("|||") if cached[3] else [],
            h2=cached[4].split("|||") if cached[4] else [],
            h3=cached[5].split("|||") if cached[5] else [],
            word_count=cached[6],
            internal_links=cached[7],
            external_links=cached[8],
            text=cached[9],
        )

    pc = PageContent(url=url)

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": config.USER_AGENT},
            timeout=config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as exc:
        pc.error = str(exc)
        return pc

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "form",
        "input",
        "button",
        "select",
        "option",
        "textarea",
        "label",
        "iframe",
        "nav",
        "footer",
        "header",
    ]):
        tag.decompose()

    pc.title = _clean(soup.title.string) if soup.title and soup.title.string else ""

    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        pc.meta_description = _clean(md["content"])

    pc.h1 = [_clean(h.get_text()) for h in soup.find_all("h1") if h.get_text(strip=True)]
    pc.h2 = [_clean(h.get_text()) for h in soup.find_all("h2") if h.get_text(strip=True)]
    pc.h3 = [_clean(h.get_text()) for h in soup.find_all("h3") if h.get_text(strip=True)]

    body = soup.find("main") or soup.find("article") or soup.find("body") or soup
    pc.text = _clean(body.get_text(separator=" "))
    pc.word_count = len(pc.text.split())

    host = urlparse(url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue

        netloc = urlparse(href).netloc

        if netloc == "" or netloc == host:
            pc.internal_links += 1
        else:
            pc.external_links += 1

    pc.ok = True
    save_cached_page(pc)

    return pc