from __future__ import annotations

import json
from pathlib import Path

from monitor_5070ti.config.settings import Settings
from monitor_5070ti.models import Source
from monitor_5070ti.notifiers.emailer import send_email
from monitor_5070ti.notifiers.telegram import send_telegram
from monitor_5070ti.sources.fetcher import fetch_source
from monitor_5070ti.utils.io import write_csv, write_json, write_latest_ai_prompt, write_markdown


def load_sources(path: Path) -> list[Source]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Source(**entry) for entry in data]


def load_keywords(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    base = Path("monitor_5070ti/config")
    settings = Settings.from_env()
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(base / "sources.json")
    keywords = load_keywords(base / "keywords.txt")

    items = []
    for src in sources:
        items.extend(fetch_source(src, keywords))

    write_json(items, settings.output_dir / "results.json")
    write_csv(items, settings.output_dir / "results.csv")
    write_markdown(items, settings.output_dir / "results.md")
    write_latest_ai_prompt(items, settings.output_dir / "latest_ai_prompt.md")

    msg = f"monitor_5070ti: {len(items)} item(s) found"
    send_telegram(settings.telegram_bot_token, settings.telegram_chat_id, msg)
    send_email(
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_user,
        settings.smtp_password,
        settings.email_from,
        settings.email_to,
        "monitor_5070ti report",
        msg,
    )
    print(msg)
    return 0
