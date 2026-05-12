from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from urllib.parse import quote_plus
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

RUB_PRICE_MAX = 130_000


@dataclass
class ProductCard:
    title: str
    price: int
    url: str
    seller: str
    availability: str
    condition: str
    source: str
    checked_at: str
    raw_text: str


class DynamicSourceRequired(RuntimeError):
    pass


class BaseSourceParser:
    source_name = "base"
    search_url = ""

    def fetch(self, query: str) -> str:
        url = self.search_url.format(query=quote_plus(query))
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    def parse(self, html: str) -> list[ProductCard]:
        raise NotImplementedError


class DNSParser(BaseSourceParser):
    source_name = "dns"
    search_url = "https://www.dns-shop.ru/search/?q={query}"

    def parse(self, html: str) -> list[ProductCard]:
        if BeautifulSoup is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards: list[ProductCard] = []
        for item in soup.select(".catalog-product"):
            title_el = item.select_one(".catalog-product__name span") or item.select_one(".catalog-product__name")
            price_el = item.select_one(".product-buy__price")
            link_el = item.select_one(".catalog-product__name")
            if not (title_el and price_el and link_el):
                continue
            price = parse_price(price_el.get_text(" ", strip=True))
            if price is None:
                continue
            url = normalize_url(link_el.get("href", ""), "https://www.dns-shop.ru")
            cards.append(make_card(title_el.get_text(" ", strip=True), price, url, "DNS", "unknown", "new", self.source_name, item.get_text(" ", strip=True)))
        return cards


class RegardParser(BaseSourceParser):
    source_name = "regard"
    search_url = "https://www.regard.ru/catalog/tovar?search={query}"

    def parse(self, html: str) -> list[ProductCard]:
        if BeautifulSoup is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards: list[ProductCard] = []
        for item in soup.select(".product-block"):
            title_el = item.select_one(".title")
            price_el = item.select_one(".price")
            link_el = item.select_one("a.title") or item.select_one("a")
            if not (title_el and price_el and link_el):
                continue
            price = parse_price(price_el.get_text(" ", strip=True))
            if price is None:
                continue
            url = normalize_url(link_el.get("href", ""), "https://www.regard.ru")
            cards.append(make_card(title_el.get_text(" ", strip=True), price, url, "Regard", "unknown", "new", self.source_name, item.get_text(" ", strip=True)))
        return cards


class CitilinkParser(BaseSourceParser):
    source_name = "citilink"
    search_url = "https://www.citilink.ru/search/?text={query}"

    def parse(self, html: str) -> list[ProductCard]:
        if BeautifulSoup is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        cards: list[ProductCard] = []
        for item in soup.select(".ProductCardVertical"):
            title_el = item.select_one(".ProductCardVertical__name")
            price_el = item.select_one("[data-meta-price]") or item.select_one(".ProductCardVerticalPrice__price-current")
            link_el = item.select_one("a.ProductCardVertical__name") or item.select_one("a")
            if not (title_el and price_el and link_el):
                continue
            price = parse_price(price_el.get_text(" ", strip=True) or price_el.get("data-meta-price", ""))
            if price is None:
                continue
            url = normalize_url(link_el.get("href", ""), "https://www.citilink.ru")
            cards.append(make_card(title_el.get_text(" ", strip=True), price, url, "Citilink", "unknown", "new", self.source_name, item.get_text(" ", strip=True)))
        return cards


class DynamicParser(BaseSourceParser):
    def parse(self, html: str) -> list[ProductCard]:
        raise DynamicSourceRequired(f"Source {self.source_name} requires dynamic browser mode (Playwright/Selenium).")


class AvitoParser(DynamicParser):
    source_name = "avito"
    search_url = "https://www.avito.ru/rossiya?q={query}"


class OzonParser(DynamicParser):
    source_name = "ozon"
    search_url = "https://www.ozon.ru/search/?text={query}"


class WildberriesParser(DynamicParser):
    source_name = "wildberries"
    search_url = "https://www.wildberries.ru/catalog/0/search.aspx?search={query}"


class YandexMarketParser(DynamicParser):
    source_name = "yandex_market"
    search_url = "https://market.yandex.ru/search?text={query}"


class MegamarketParser(DynamicParser):
    source_name = "megamarket"
    search_url = "https://megamarket.ru/catalog/?q={query}"


def parse_price(text: str) -> int | None:
    nums = re.findall(r"\d+", text.replace("\xa0", " "))
    if not nums:
        return None
    return int("".join(nums))


def normalize_url(url: str, base: str) -> str:
    if url.startswith("http"):
        return url
    if not url:
        return base
    if not url.startswith("/"):
        url = "/" + url
    return base.rstrip("/") + url


def make_card(title: str, price: int, url: str, seller: str, availability: str, condition: str, source: str, raw_text: str) -> ProductCard:
    return ProductCard(title=title.strip(), price=price, url=url, seller=seller, availability=availability, condition=condition, source=source, checked_at=datetime.now(timezone.utc).isoformat(), raw_text=raw_text[:4000])


def is_valid_product(card: ProductCard) -> bool:
    title = card.title.lower()
    if "5070" not in title or "ti" not in title:
        return False
    if "4070 ti" in title or "3070 ti" in title:
        return False
    banned = ["ноутбук", "laptop", "ноут", "pc", "сбор", "системный блок", "waterblock", "водоблок", "cooler", "кулер", "кабель", "держател", "аксессуар"]
    if any(k in title for k in banned):
        return False
    if card.price <= 0 or card.price > RUB_PRICE_MAX:
        return False
    return True


def run_monitor(query: str = "RTX 5070 Ti", report_dir: Path = Path("reports"), dynamic_mode: str = "off") -> list[ProductCard]:
    parsers: list[BaseSourceParser] = [DNSParser(), RegardParser(), CitilinkParser(), AvitoParser(), OzonParser(), WildberriesParser(), YandexMarketParser(), MegamarketParser()]
    accepted: list[ProductCard] = []
    for parser in parsers:
        try:
            html = parser.fetch(query)
            cards = parser.parse(html)
            accepted.extend([c for c in cards if is_valid_product(c)])
        except DynamicSourceRequired as exc:
            logging.warning("%s", exc)
            if dynamic_mode == "playwright":
                logging.warning("Playwright mode selected but fallback parser is not implemented for %s", parser.source_name)
        except Exception as exc:
            logging.exception("failed source %s: %s", parser.source_name, exc)

    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    data_path = report_dir / f"report_{timestamp}.json"
    text_path = report_dir / f"report_{timestamp}.txt"
    data_path.write_text(json.dumps([asdict(c) for c in accepted], ensure_ascii=False, indent=2), encoding="utf-8")
    text_path.write_text("\n".join(f"{c.price} | {c.title} | {c.url}" for c in accepted), encoding="utf-8")
    return accepted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="RTX 5070 Ti")
    parser.add_argument("--dynamic-mode", choices=["off", "playwright", "selenium"], default="off")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    cards = run_monitor(query=args.query, dynamic_mode=args.dynamic_mode)
    logging.info("found %s cards", len(cards))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
