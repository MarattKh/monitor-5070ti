from __future__ import annotations

from typing import Iterable

import requests
from bs4 import BeautifulSoup

from monitor_5070ti.models import Item, Source


USER_AGENT = "Mozilla/5.0 (monitor_5070ti; +https://localhost)"


def fetch_source(source: Source, keywords: Iterable[str], timeout: int = 15) -> list[Item]:
    if source.requires_playwright:
        return [
            Item(
                source=source.name,
                url=source.url,
                title="Requires Playwright fallback",
                snippet="Source marked unstable for requests; parse with Playwright.",
                matched_keywords=[],
                requires_playwright=True,
            )
        ]

    try:
        resp = requests.get(source.url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
    except requests.RequestException as exc:
        return [
            Item(
                source=source.name,
                url=source.url,
                title="Request failed",
                snippet=str(exc),
                matched_keywords=[],
                requires_playwright=True,
            )
        ]

    soup = BeautifulSoup(resp.text, "html.parser")
    text = " ".join(soup.stripped_strings)
    found = [kw for kw in keywords if kw.lower() in text.lower()]
    if not found:
        return []

    title = soup.title.string.strip() if soup.title and soup.title.string else source.name
    snippet = text[:280]
    return [Item(source=source.name, url=source.url, title=title, snippet=snippet, matched_keywords=found)]
