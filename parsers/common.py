from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen

from models import ProductOffer

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PRICE_RE = re.compile(r"(\d[\d\s]{2,9})\s?(₽|руб|RUB)", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")


def parse_rub(value: str) -> float | None:
    digits = re.sub(r"[^\d]", "", value)
    return float(digits) if digits else None


def _download(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=20) as r:  # nosec B310
        return r.read().decode("utf-8", errors="ignore")


def scrape_search_page(source: str, url: str, seller: str = "") -> list[ProductOffer]:
    try:
        html = _download(url)
    except URLError:
        return []
    text = TAG_RE.sub(" ", html)
    matches = list(PRICE_RE.finditer(text))
    now = datetime.now(timezone.utc).isoformat()
    offers: list[ProductOffer] = []
    for m in matches[:8]:
        price = parse_rub(m.group(1))
        if not price:
            continue
        chunk = text[max(0, m.start()-180): m.end()+180]
        cond = "used" if any(x in chunk.lower() for x in ["б/у", "used"]) else "new"
        offers.append(ProductOffer(source, "RTX 5070 Ti", price, "RUB", url, cond, seller or source, "unknown", now, 0.4, chunk))
    return offers
