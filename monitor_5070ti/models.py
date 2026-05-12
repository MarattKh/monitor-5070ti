from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Source:
    name: str
    url: str
    requires_playwright: bool = False


@dataclass(slots=True)
class Item:
    source: str
    url: str
    title: str
    snippet: str
    matched_keywords: list[str]
    requires_playwright: bool = False
