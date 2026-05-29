from models import ProductOffer
from tools.offer_deduplication import deduplicate_offers, normalize_offer_url


def mk_offer(title: str, price: float, url: str, source: str = "DNS") -> ProductOffer:
    return ProductOffer(
        source,
        title,
        price,
        "RUB",
        url,
        "new",
        source,
        "in_stock",
        "2026-01-01T00:00:00+00:00",
        0.9,
        title,
    )


def test_normalize_offer_url_ignores_tracking_params_and_fragment():
    assert normalize_offer_url("HTTPS://Example.COM/product/1/?utm_source=tg&gclid=abc&foo=bar#reviews") == "https://example.com/product/1?foo=bar"


def test_deduplicate_offers_by_normalized_url_keeps_cheapest_offer():
    offers = [
        mk_offer("RTX 5070 Ti expensive duplicate", 91000, "https://shop.example/product/1?utm_source=tg"),
        mk_offer("RTX 5070 Ti cheaper duplicate", 89000, "https://shop.example/product/1"),
    ]

    result = deduplicate_offers(offers)

    assert len(result) == 1
    assert result[0].title == "RTX 5070 Ti cheaper duplicate"
    assert result[0].price == 89000


def test_deduplicate_offers_by_source_title_price_fallback_when_url_is_empty():
    offers = [
        mk_offer("Palit RTX 5070 Ti GamingPro", 92500, "", source="Регард"),
        mk_offer("Palit  RTX-5070-Ti GamingPro", 92500, "", source="Регард"),
    ]

    result = deduplicate_offers(offers)

    assert len(result) == 1
    assert result[0].source == "Регард"
    assert result[0].price == 92500


def test_deduplicate_offers_keeps_distinct_offers_with_same_price():
    offers = [
        mk_offer("Palit RTX 5070 Ti GamingPro", 92500, "https://shop.example/product/1"),
        mk_offer("Gigabyte RTX 5070 Ti Windforce", 92500, "https://shop.example/product/2"),
    ]

    result = deduplicate_offers(offers)

    assert [offer.title for offer in result] == [
        "Gigabyte RTX 5070 Ti Windforce",
        "Palit RTX 5070 Ti GamingPro",
    ]
