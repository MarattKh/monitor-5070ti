from __future__ import annotations

import csv
import json
from pathlib import Path

from monitor_5070ti.models import Item


def write_json(items: list[Item], path: Path) -> None:
    path.write_text(json.dumps([item.__dict__ for item in items], ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(items: list[Item], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["source", "url", "title", "snippet", "matched_keywords", "requires_playwright"]
        )
        writer.writeheader()
        for item in items:
            row = item.__dict__.copy()
            row["matched_keywords"] = ", ".join(item.matched_keywords)
            writer.writerow(row)


def write_markdown(items: list[Item], path: Path) -> None:
    lines = ["# monitor_5070ti results", ""]
    for item in items:
        lines.append(f"## {item.title}")
        lines.append(f"- Source: {item.source}")
        lines.append(f"- URL: {item.url}")
        lines.append(f"- Keywords: {', '.join(item.matched_keywords) if item.matched_keywords else '-'}")
        lines.append(f"- requires_playwright: {item.requires_playwright}")
        lines.append("")
        lines.append(item.snippet)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_latest_ai_prompt(items: list[Item], path: Path) -> None:
    summary = "\n".join(f"- [{i.source}] {i.title}: {i.url}" for i in items)
    text = (
        "You are an analyst. Summarize updates about RTX 5070 Ti from the items below, "
        "highlighting price, availability, and benchmarks.\n\n"
        f"{summary}\n"
    )
    path.write_text(text, encoding="utf-8")
