from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.error import URLError

from models import ProductOffer
from parsers.browser import fetch_html
from parsers.common import _download, _clean_text, parse_rub

CARD_RE = re.compile(r'(<div[^>]+class="[^"]*catalog-product[^"]*"[^>]*>.*?</div>\s*</div>)', re.S)
TITLE_RE = re.compile(r'class="[^"]*catalog-product__name[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
PRICE_RE = re.compile(r'class="[^"]*product-buy__price[^"]*"[^>]*>(.*?)</', re.S)
AVAIL_RE = re.compile(r'class="[^"]*(?:order-avail-wrap|product-buy__avail)[^"]*"[^>]*>(.*?)</', re.S)
DNS_BLOCK_WARNING = "DNS access forbidden. Manual verification required."


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


def detect_block_reason(html: str) -> str | None:
    normalized = html.lower()
    if "403 forbidden" in normalized or "доступ к сайту запрещен" in normalized:
        return "403 forbidden"
    return None


def _build_offers(html: str) -> list[ProductOffer]:
    now = datetime.now(timezone.utc).isoformat()
    offers: list[ProductOffer] = []
    for c in parse_cards(html):
        full_url = c["url"] if c["url"].startswith("http") else f"https://www.dns-shop.ru{c['url']}"
        offers.append(ProductOffer("DNS", c["title"], c["price"], "RUB", full_url, "new", "DNS", c["availability"], now, 0.85, c["title"]))
    return offers


def parse_offers_with_status(browser_mode: bool = False) -> dict:
    search_url = "https://www.dns-shop.ru/search/?q=rtx+5070+ti"
    try:
        html = fetch_html(search_url, save_to="debug_html/dns.html") if browser_mode else _download(search_url)
    except URLError as exc:
        code = getattr(exc, "code", None)
        if code in (401, 403):
            return {
                "offers": [],
                "blocked": True,
                "block_reason": "401 unauthorized" if code == 401 else "403 forbidden",
                "warnings": [DNS_BLOCK_WARNING],
                "errors": 1,
            }
        warning = str(exc) or "DNS download failed."
        return {
            "offers": [],
            "blocked": False,
            "block_reason": None,
            "warnings": [warning],
            "errors": 1,
        }

    block_reason = detect_block_reason(html)
    if block_reason:
        return {
            "offers": [],
            "blocked": True,
            "block_reason": block_reason,
            "warnings": [DNS_BLOCK_WARNING],
            "errors": 1,
        }

    return {
        "offers": _build_offers(html),
        "blocked": False,
        "block_reason": None,
        "warnings": [],
        "errors": 0,
    }


def parse_offers(browser_mode: bool = False) -> list[ProductOffer]:
    return parse_offers_with_status(browser_mode)["offers"]
