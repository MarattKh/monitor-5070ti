from pathlib import Path

from monitor_5070_ti_v_2 import ProductCard, is_valid_product, run_monitor


def card(title: str, price: int = 100000):
    return ProductCard(title=title, price=price, url="https://example.com/item", seller="x", availability="in stock", condition="new", source="test", checked_at="2026-01-01T00:00:00+00:00", raw_text=title)


def test_filter_accepts_rtx_5070_ti():
    assert is_valid_product(card("Видеокарта GeForce RTX 5070 Ti 16GB"))


def test_filter_rejects_rtx_5070_without_ti():
    assert not is_valid_product(card("Видеокарта GeForce RTX 5070 12GB"))


def test_filter_rejects_laptop():
    assert not is_valid_product(card("Ноутбук игровой RTX 5070 Ti"))


def test_filter_rejects_waterblock():
    assert not is_valid_product(card("Водоблок для RTX 5070 Ti"))


def test_reports_are_created(tmp_path: Path):
    cards = run_monitor(report_dir=tmp_path)
    assert isinstance(cards, list)
    assert list(tmp_path.glob("report_*.json"))
    assert list(tmp_path.glob("report_*.txt"))


def test_import_main():
    import monitor_5070_ti_v_2  # noqa: F401
