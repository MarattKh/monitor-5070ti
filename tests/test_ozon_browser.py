from parsers import ozon


BLOCKED_HTML = """
<html lang="ru">
  <head>
    <link rel="stylesheet" href="https://cdn2.ozone.ru/s3/abt-challenge/incidents/styles_v2/common.css">
    <title>Подождите, вас проверяем</title>
  </head>
  <body>
    <span class="subtitle">We need to make sure that you are not a robot.</span>
    <span class="details-text"><b>ID:</b> fab_chlg_20260604161626_01KT9PQXGX247V0PCMEQG6WP1Z</span>
  </body>
</html>
"""

FIXTURE_HTML = """
<html>
  <body>
    <div class="tile-root">
      <a href="/product/gigabyte-geforce-rtx-5070-ti-windforce-16g-123/">
        <span class="tile-hover-target">Gigabyte GeForce RTX 5070 Ti WINDFORCE 16G</span>
      </a>
      <span class="price">99 490 RUB</span>
    </div>
    <div class="tile-root">
      <a href="/product/gigabyte-geforce-rtx-5070-windforce-16g-456/">
        <span class="tile-hover-target">Gigabyte GeForce RTX 5070 WINDFORCE 16G</span>
      </a>
      <span class="price">76 990 RUB</span>
    </div>
    <div class="tile-root">
      <a href="/product/ventilator-rtx-5070-ti-789/">
        <span class="tile-hover-target">Вентилятор для GeForce RTX 5070 Ti</span>
      </a>
      <span class="price">4 990 RUB</span>
    </div>
  </body>
</html>
"""


def test_parse_browser_html_extracts_rtx_5070_ti_offer():
    offers = ozon.parse_browser_html(FIXTURE_HTML)

    assert len(offers) == 1
    assert offers[0].source == "Ozon"
    assert offers[0].title == "Gigabyte GeForce RTX 5070 Ti WINDFORCE 16G"
    assert offers[0].price == 99490
    assert offers[0].url == "https://www.ozon.ru/product/gigabyte-geforce-rtx-5070-ti-windforce-16g-123/"


def test_parse_browser_html_rejects_non_rtx_and_accessory():
    offers = ozon.parse_browser_html(FIXTURE_HTML)

    titles = [offer.title for offer in offers]
    assert "Gigabyte GeForce RTX 5070 WINDFORCE 16G" not in titles
    assert "Вентилятор для GeForce RTX 5070 Ti" not in titles


def test_parse_browser_html_returns_empty_for_abt_challenge():
    assert ozon.parse_browser_html(BLOCKED_HTML) == []


def test_detect_block_reason_identifies_abt_challenge():
    assert ozon.detect_block_reason(BLOCKED_HTML) == "antibot challenge (abt-challenge)"


def test_detect_block_reason_returns_none_for_normal_html():
    assert ozon.detect_block_reason(FIXTURE_HTML) is None


def test_detect_block_reason_identifies_403():
    html = "<html><body>403 Forbidden. Access denied.</body></html>"
    assert ozon.detect_block_reason(html) == "403 forbidden"


def test_parse_offers_with_status_returns_blocked_for_abt_challenge(monkeypatch):
    monkeypatch.setattr(ozon, "fetch_html", lambda *args, **kwargs: BLOCKED_HTML)

    result = ozon.parse_offers_with_status(browser_mode=True)

    assert result == {
        "offers": [],
        "blocked": True,
        "block_reason": "antibot challenge (abt-challenge)",
        "warnings": [ozon.OZON_BLOCK_WARNING],
        "errors": 1,
    }


def test_parse_offers_with_status_returns_offers_for_valid_html(monkeypatch):
    monkeypatch.setattr(ozon, "fetch_html", lambda *args, **kwargs: FIXTURE_HTML)

    result = ozon.parse_offers_with_status(browser_mode=True)

    assert result["blocked"] is False
    assert result["block_reason"] is None
    assert result["errors"] == 0
    assert len(result["offers"]) == 1
    assert result["offers"][0].source == "Ozon"


def test_parse_offers_with_status_http_error_treated_as_blocked(monkeypatch):
    from urllib.error import HTTPError

    def raise_403(url):
        raise HTTPError(url, 403, "Forbidden", hdrs=None, fp=None)

    monkeypatch.setattr(ozon, "_download", raise_403)

    result = ozon.parse_offers_with_status(browser_mode=False)

    assert result["blocked"] is True
    assert result["block_reason"] == "403 forbidden"
    assert result["warnings"] == [ozon.OZON_BLOCK_WARNING]
    assert result["errors"] == 1
    assert result["offers"] == []

