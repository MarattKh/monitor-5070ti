from __future__ import annotations

import html as html_lib
import re
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from models import ProductOffer

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PRICE_RE = re.compile(r"(\d[\d\s]{2,9})\s?(₽|руб|RUB)", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
HREF_RE = re.compile(r"href=[\"\']([^\"\']+)[\"\']", re.IGNORECASE)


def parse_rub(value: str) -> float | None:
    digits = re.sub(r"[^\d]", "", value)
    return float(digits) if digits else None


def _download(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=6) as r:  # nosec B310
        return r.read().decode("utf-8", errors="ignore")


def _clean_text(fragment: str) -> str:
    plain = TAG_RE.sub(" ", fragment)
    plain = html_lib.unescape(plain)
    return " ".join(plain.split())


def _is_search_url(url: str) -> bool:
    u = url.lower()
    return "?q=" in u or "?text=" in u or "/search" in u


def extract_product_offers(source: str, search_url: str, seller: str = "") -> list[ProductOffer]:
    try:
        page = _download(search_url)
    except URLError:
        return []

    now = datetime.now(timezone.utc).isoformat()
    offers: list[ProductOffer] = []

    for m in PRICE_RE.finditer(page):
        price = parse_rub(m.group(1))
        if not price:
            continue
        start = max(0, m.start() - 800)
        end = min(len(page), m.end() + 800)
        chunk_html = page[start:end]

        href_match = HREF_RE.search(chunk_html)
        if not href_match:
            continue
        card_url = urljoin(search_url, href_match.group(1).strip())
        if _is_search_url(card_url):
            continue

        title = _clean_text(chunk_html)
        if len(title) < 5:
            continue

        lowered = title.lower()
        condition = "used" if any(x in lowered for x in ["б/у", "used"]) else "new"
        availability = "in_stock" if any(x in lowered for x in ["в наличии", "доставка", "купить"]) else "unknown"

        offers.append(
            ProductOffer(
                source=source,
                title=title[:220],
                price=price,
                currency="RUB",
                url=card_url,
                condition=condition,
                seller=seller or source,
                availability=availability,
                checked_at=now,
                confidence=0.55,
                raw_text=title[:1000],
            )
        )
        if len(offers) >= 20:
            break

    return offers


def scrape_search_page(source: str, url: str, seller: str = "") -> list[ProductOffer]:
    return extract_product_offers(source=source, search_url=url, seller=seller)
