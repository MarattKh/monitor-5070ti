from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _price(record: dict[str, Any]) -> float | None:
    value = record.get("price")
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_price(value: float, currency: Any) -> str:
    amount = f"{value:.0f}" if value.is_integer() else f"{value:.2f}"
    return f"{amount} {currency or 'RUB'}"


def _format_offer(record: dict[str, Any]) -> str:
    price = _price(record)
    if price is None:
        return "n/a"

    parts = [
        _format_price(price, record.get("currency")),
        str(record.get("source") or "unknown"),
    ]
    title = record.get("title")
    if title:
        parts.append(str(title))
    url = record.get("url")
    if url:
        parts.append(str(url))
    return " | ".join(parts)


def load_history(path: str | Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    invalid_json_lines = 0

    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                invalid_json_lines += 1
                continue
            if isinstance(record, dict):
                records.append(record)

    return records, invalid_json_lines


def best_current_by_source(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    current: dict[str, dict[str, Any]] = {}

    for source in sorted({str(r.get("source") or "unknown") for r in records}):
        priced = [r for r in records if str(r.get("source") or "unknown") == source and _price(r) is not None]
        if not priced:
            continue
        latest_timestamp = max(str(r.get("timestamp") or "") for r in priced)
        latest_records = [r for r in priced if str(r.get("timestamp") or "") == latest_timestamp]
        current[source] = min(latest_records, key=lambda r: (_price(r) or float("inf"), str(r.get("title") or "")))

    return current


def format_summary(records: list[dict[str, Any]], invalid_json_lines: int = 0) -> str:
    lines = [
        "Price history summary",
        f"Records: {len(records)}",
    ]
    if invalid_json_lines:
        lines.append(f"Warning: ignored invalid JSON lines: {invalid_json_lines}")

    timestamps = [str(r.get("timestamp")) for r in records if r.get("timestamp")]
    lines.append(f"Latest timestamp: {max(timestamps) if timestamps else 'n/a'}")

    current = best_current_by_source(records)
    lines.append("Best current known price by source:")
    if current:
        for source in sorted(current):
            lines.append(f"- {source}: {_format_offer(current[source])}")
    else:
        lines.append("- n/a")

    priced_records = [r for r in records if _price(r) is not None]
    best = min(priced_records, key=lambda r: (_price(r) or float("inf"), str(r.get("source") or ""), str(r.get("title") or ""))) if priced_records else None
    lines.append(f"Best overall price: {_format_offer(best) if best else 'n/a'}")

    signal_counts = Counter(str(r.get("signal") or "UNKNOWN") for r in records)
    lines.append("Signal counts:")
    if signal_counts:
        for signal in sorted(signal_counts):
            lines.append(f"- {signal}: {signal_counts[signal]}")
    else:
        lines.append("- n/a")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize a JSONL price history file.")
    parser.add_argument("path", nargs="?", default="price_history.jsonl", help="Path to price_history.jsonl")
    args = parser.parse_args(argv)

    records, invalid_json_lines = load_history(args.path)
    print(format_summary(records, invalid_json_lines), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
