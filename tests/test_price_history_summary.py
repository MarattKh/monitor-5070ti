import json

from tools import price_history_summary


def write_jsonl(path, records, extra_lines=None):
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    if extra_lines:
        lines.extend(extra_lines)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_format_summary_reports_counts_best_prices_and_latest_timestamp(tmp_path):
    history_path = tmp_path / "price_history.jsonl"
    write_jsonl(
        history_path,
        [
            {
                "timestamp": "2026-05-28T08:00:00+00:00",
                "source": "DNS",
                "title": "Old DNS",
                "price": 89000,
                "currency": "RUB",
                "url": "https://example.test/old",
                "signal": "GOOD_PRICE",
            },
            {
                "timestamp": "2026-05-29T08:00:00+00:00",
                "source": "DNS",
                "title": "Current DNS",
                "price": 91000,
                "currency": "RUB",
                "url": "https://example.test/current",
                "signal": "NORMAL",
            },
            {
                "timestamp": "2026-05-29T07:00:00+00:00",
                "source": "Ситилинк",
                "title": "Best overall",
                "price": 78000,
                "currency": "RUB",
                "url": "https://example.test/best",
                "signal": "URGENT_BUY",
            },
        ],
    )

    records, invalid_json_lines = price_history_summary.load_history(history_path)
    output = price_history_summary.format_summary(records, invalid_json_lines)

    assert "Records: 3" in output
    assert "Latest timestamp: 2026-05-29T08:00:00+00:00" in output
    assert "- DNS: 91000 RUB | DNS | Current DNS | https://example.test/current" in output
    assert "- Ситилинк: 78000 RUB | Ситилинк | Best overall | https://example.test/best" in output
    assert "Best overall price: 78000 RUB | Ситилинк | Best overall | https://example.test/best" in output
    assert "- GOOD_PRICE: 1" in output
    assert "- NORMAL: 1" in output
    assert "- URGENT_BUY: 1" in output


def test_invalid_json_lines_are_counted_without_crashing(tmp_path, capsys):
    history_path = tmp_path / "price_history.jsonl"
    write_jsonl(
        history_path,
        [
            {
                "timestamp": "2026-05-29T08:00:00+00:00",
                "source": "DNS",
                "title": "Valid offer",
                "price": 90000,
                "currency": "RUB",
                "signal": "GOOD_PRICE",
            }
        ],
        extra_lines=["not json", "{\"timestamp\": "],
    )

    result = price_history_summary.main([str(history_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "Records: 1" in captured.out
    assert "Warning: ignored invalid JSON lines: 2" in captured.out
    assert "Valid offer" in captured.out
    assert captured.err == ""


def test_empty_history_summary_is_concise():
    output = price_history_summary.format_summary([])

    assert output == (
        "Price history summary\n"
        "Records: 0\n"
        "Latest timestamp: n/a\n"
        "Best current known price by source:\n"
        "- n/a\n"
        "Best overall price: n/a\n"
        "Signal counts:\n"
        "- n/a\n"
    )
