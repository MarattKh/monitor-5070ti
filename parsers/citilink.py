from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.error import URLError

from models import ProductOffer
from parsers.common import _download, _clean_text, parse_rub

CARD_RE = re.compile(r'(<article[^>]+class="[^"]*product-card[^"]*"[^>]*>.*?</article>)', re.S)
TITLE_RE = re.compile(r'class="[^"]*ProductCardHorizontal__title[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
PRICE_RE = re.compile(r'class="[^"]*ProductCardHorizontal__price_current-price[^"]*"[^>]*>(.*?)</', re.S)
AVAIL_RE = re.compile(r'class="[^"]*ProductCardHorizontal__availability[^"]*"[^>]*>(.*?)</', re.S)


def parse_cards(html: str) -> list[dict]:
    cards: list[dict] = []
    for block in CARD_RE.findall(html):
        t = TITLE_RE.search(block)
        p = PRICE_RE.search(block)
        if not t or not p:
            continue
        url = t.group(1)
        title = _clean_text(t.group(2))
        price = parse_rub(_clean_text(p.group(1)))
        if not price or not title:
            continue
        av = AVAIL_RE.search(block)
        availability = _clean_text(av.group(1)) if av else "unknown"
        cards.append({"title": title, "url": url, "price": price, "availability": availability})
    return cards


def parse_offers() -> list[ProductOffer]:
    search_url = "https://www.citilink.ru/search/?text=rtx%205070%20ti"
    try:
        html = _download(search_url)
    except URLError:
        return []
    now = datetime.now(timezone.utc).isoformat()
    offers: list[ProductOffer] = []
    for c in parse_cards(html):
        full_url = c["url"] if c["url"].startswith("http") else f"https://www.citilink.ru{c['url']}"
        offers.append(ProductOffer("Ситилинк", c["title"], c["price"], "RUB", full_url, "new", "Ситилинк", c["availability"], now, 0.85, c["title"]))
    return offers
