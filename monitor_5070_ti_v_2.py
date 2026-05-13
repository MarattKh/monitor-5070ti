from __future__ import annotations

import csv
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from models import ProductOffer

from parsers import (
    aliexpress,
    avito,
    cdek_shopping,
    computeruniverse,
    dns,
    eldorado,
    mvideo,
    megamarket,
    ozon,
    regard,
    citilink,
    wildberries,
    yandex_market,
)

MAX_PRICE_RUB = 130_000



def configure_logging() -> None:
    logging.basicConfig(
        filename="monitor.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )


def normalize_title(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def is_rtx_5070_ti(title: str, raw_text: str) -> bool:
    haystack = normalize_title(f"{title} {raw_text}")
    has_5070 = "5070" in haystack
    has_ti = "ti" in haystack or "ti," in haystack
    return has_5070 and has_ti


def is_accessory_or_invalid(title: str, raw_text: str) -> bool:
    haystack = normalize_title(f"{title} {raw_text}")
    bad_keywords = [
        "rtx 5070" ,"5070 super",
        "кабель",
        "переходник",
        "кулер",
        "водоблок",
        "ноутбук",
        "laptop",
        "компьютер",
        "системный блок",
        "pc",
        "корпус",
        "держатель",
        "подставка",
        "чехол",
        "fan",
    ]
    if "5070 ti" not in haystack and "5070ti" not in haystack:
        return True
    return any(x in haystack for x in bad_keywords if x != "rtx 5070") and "5070 ti" not in haystack


def filter_offers(offers: Iterable[ProductOffer]) -> list[ProductOffer]:
    out: list[ProductOffer] = []
    for item in offers:
        if item.price <= 0:
            continue
        if item.currency.upper() != "RUB":
            continue
        if item.price > MAX_PRICE_RUB:
            continue
        if not is_rtx_5070_ti(item.title, item.raw_text):
            continue
        if is_accessory_or_invalid(item.title, item.raw_text):
            continue
        if "5070 ti" not in normalize_title(item.title + " " + item.raw_text):
            continue
        out.append(item)
    out.sort(key=lambda x: x.price)
    return out


def classify_signal(item: ProductOffer) -> str | None:
    c = item.condition.lower()
    if c == "new":
        if item.price <= 75_000:
            return "urgent_buy"
        if item.price <= 90_000:
            return "good_price"
    if c == "used":
        if item.price <= 50_000:
            return "urgent_buy"
        if item.price <= 65_000:
            return "good_price"
    return None


def render_markdown(offers: list[ProductOffer]) -> str:
    lines = [
        "# RTX 5070 Ti offers",
        "",
        "| Source | Title | Price | Condition | Availability | URL |",
        "|---|---|---:|---|---|---|",
    ]
    for o in offers:
        lines.append(
            f"| {o.source} | {o.title.replace('|', '/')} | {o.price:.0f} {o.currency} | {o.condition} | {o.availability} | {o.url} |"
        )
    return "\n".join(lines) + "\n"


def save_reports(offers: list[ProductOffer]) -> None:
    Path("results.json").write_text(
        json.dumps([asdict(x) for x in offers], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(offers[0]).keys()) if offers else [
            "source","title","price","currency","url","condition","seller","availability","checked_at","confidence","raw_text"
        ])
        w.writeheader()
        for x in offers:
            w.writerow(asdict(x))

    Path("results.md").write_text(render_markdown(offers), encoding="utf-8")

    urgent = [o for o in offers if classify_signal(o) == "urgent_buy"]
    Path("urgent_deals.md").write_text(render_markdown(urgent), encoding="utf-8")

    prompt = (
        "Проанализируй список предложений RTX 5070 Ti, выдели аномально дешевые, "
        "проверь возможные риски продавца и предложи стратегию покупки."
    )
    Path("latest_ai_prompt.md").write_text(prompt + "\n", encoding="utf-8")


def notify_telegram(offers: list[ProductOffer]) -> None:
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        import requests

        interesting = [o for o in offers if classify_signal(o) in {"good_price", "urgent_buy"}]
        if not interesting:
            return
        rows = [f"{o.source}: {o.title} — {o.price:.0f} RUB ({classify_signal(o)})\n{o.url}" for o in interesting]
        text = "⚡ RTX 5070 Ti сигналы:\n\n" + "\n\n".join(rows[:10])
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text[:4000]},
            timeout=15,
        )
    except Exception as exc:
        logging.getLogger("telegram").exception("telegram error: %s", exc)


def run_source(name: str, fn) -> list[ProductOffer]:
    logger = logging.getLogger(name)
    try:
        return fn.parse_offers()
    except Exception as exc:
        logger.exception("source failed: %s", exc)
        return []


def main() -> None:
    configure_logging()
    sources = {
        "DNS": dns,
        "Ситилинк": citilink,
        "Регард": regard,
        "Ozon": ozon,
        "Wildberries": wildberries,
        "М.Видео": mvideo,
        "Эльдорадо": eldorado,
        "Яндекс Маркет": yandex_market,
        "Avito": avito,
        "Мегамаркет": megamarket,
        "AliExpress": aliexpress,
        "ComputerUniverse": computeruniverse,
        "CDEK.Shopping": cdek_shopping,
    }
    collected: list[ProductOffer] = []
    for name, module in sources.items():
        collected.extend(run_source(name, module))
    filtered = filter_offers(collected)
    save_reports(filtered)
    notify_telegram(filtered)
    print(f"Done. Total offers after filter: {len(filtered)}")


if __name__ == "__main__":
    main()
