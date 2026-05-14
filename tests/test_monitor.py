from pathlib import Path

from monitor_5070_ti_v_2 import filter_offers
from models import ProductOffer
from parsers.citilink import parse_cards as parse_citilink_cards
from parsers.dns import parse_cards as parse_dns_cards
from parsers.regard import parse_cards as parse_regard_cards


def mk_offer(title: str, raw: str = "", price: float = 100000, url: str = "https://example.com/product/1") -> ProductOffer:
    return ProductOffer("DNS", title, price, "RUB", url, "new", "DNS", "in_stock", "2026-01-01T00:00:00+00:00", 0.9, raw)


def test_accepts_rtx_5070_ti():
    offers = filter_offers([mk_offer("NVIDIA GeForce RTX 5070 Ti")])
    assert len(offers) == 1


def test_accepts_rtx5070ti_without_spaces():
    offers = filter_offers([mk_offer("MSI RTX5070Ti Gaming")])
    assert len(offers) == 1


def test_rejects_rtx_5070_without_ti():
    offers = filter_offers([mk_offer("NVIDIA GeForce RTX 5070")])
    assert offers == []


def test_rejects_laptop():
    offers = filter_offers([mk_offer("RTX 5070 Ti laptop")])
    assert offers == []


def test_rejects_desktop_pc():
    offers = filter_offers([mk_offer("Gaming PC RTX 5070 Ti")])
    assert offers == []


def test_rejects_waterblock():
    offers = filter_offers([mk_offer("Waterblock for RTX 5070 Ti")])
    assert offers == []


def test_reports_are_created(tmp_path, monkeypatch):
    import monitor_5070_ti_v_2 as mon

    monkeypatch.chdir(tmp_path)
    mon.save_reports([mk_offer("RTX 5070 Ti Ventus", price=89000)], [{"source": "DNS", "raw_count": 1, "filtered_count": 1, "error": ""}])

    assert Path("results.json").exists()
    assert Path("results.csv").exists()
    assert Path("results.md").exists()
    assert Path("urgent_deals.md").exists()
    assert Path("latest_ai_prompt.md").exists()


def test_source_summary_counts_and_errors():
    import monitor_5070_ti_v_2 as mon

    ok_offer = mk_offer("RTX 5070 Ti", url="https://shop.example/product/5070ti")

    offers, err = mon.run_source(
        "DNS",
        lambda: [
            ok_offer,
            mk_offer("RTX 5070", url="https://shop.example/product/5070"),
        ],
    )
    assert err == ""
    assert len(offers) == 2
    assert len(mon.filter_offers(offers)) == 1

    offers_bad, err_bad = mon.run_source(
        "DNS",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert offers_bad == []
    assert "boom" in err_bad


def test_results_md_contains_summary_and_source_summary(tmp_path, monkeypatch):
    import monitor_5070_ti_v_2 as mon

    monkeypatch.chdir(tmp_path)
    mon.save_reports(
        [mk_offer("RTX 5070 Ti Ventus", price=89000)],
        [{"source": "DNS", "raw_count": 3, "filtered_count": 1, "error": ""}],
    )

    content = Path("results.md").read_text(encoding="utf-8")
    assert "## Summary" in content
    assert "## Source summary" in content
    assert "| DNS | 3 | 1 |  |" in content


def test_no_search_urls_in_results():
    offers = [
        mk_offer("RTX 5070 Ti", url="https://shop.example/search/?q=rtx+5070+ti"),
        mk_offer("RTX 5070 Ti", url="https://shop.example/product/5070ti"),
    ]
    filtered = filter_offers(offers)
    assert all("/search" not in x.url and "?q=" not in x.url and "?text=" not in x.url for x in filtered)


def test_title_is_not_artificial():
    title = "Palit GeForce RTX 5070 Ti GameRock OC"
    offers = [mk_offer(title)]
    filtered = filter_offers(offers)
    assert filtered and filtered[0].title != "RTX 5070 Ti"


def test_dns_fixture_card_parsing_and_filtering():
    html = Path("tests/fixtures/dns_search.html").read_text(encoding="utf-8")
    cards = parse_dns_cards(html)
    offers = [mk_offer(c["title"], price=c["price"], url=f"https://www.dns-shop.ru{c['url']}") for c in cards]
    filtered = filter_offers(offers)
    assert filtered
    assert "Palit" in filtered[0].title
    assert "/search" not in filtered[0].url and "?q=" not in filtered[0].url and "?text=" not in filtered[0].url
    assert filtered[0].price == 89999
    assert all("РІРѕРґРѕР±Р»РѕРє" not in x.title.lower() for x in filtered)
    assert all(" 5070" not in x.title.lower() or "ti" in x.title.lower() for x in filtered)


def test_regard_fixture_card_parsing_and_filtering():
    html = Path("tests/fixtures/regard_search.html").read_text(encoding="utf-8")
    cards = parse_regard_cards(html)
    offers = [mk_offer(c["title"], price=c["price"], url=f"https://www.regard.ru{c['url']}") for c in cards]
    filtered = filter_offers(offers)
    assert len(filtered) == 1
    assert "Windforce" in filtered[0].title
    assert "/product/737606/" in filtered[0].url
    assert filtered[0].price == 92500


def test_citilink_fixture_card_parsing_and_filtering():
    html = Path("tests/fixtures/citilink_search.html").read_text(encoding="utf-8")
    cards = parse_citilink_cards(html)
    offers = [mk_offer(c["title"], price=c["price"], url=f"https://www.citilink.ru{c['url']}") for c in cards]
    filtered = filter_offers(offers)
    assert len(filtered) == 1
    assert "5070" in filtered[0].title
    assert "TI" in filtered[0].title.upper()
    assert "/search" not in filtered[0].url and "?q=" not in filtered[0].url and "?text=" not in filtered[0].url
    assert filtered[0].price == 100730