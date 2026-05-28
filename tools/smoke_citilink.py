from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from parsers import citilink
from parsers.common import UA, _clean_text


DEFAULT_TIMEOUT_SECONDS = 8

PRODUCT_LINK_RE = re.compile(r'href="[^"]*/product/[^"]+"', re.I)

SIGN_PATTERNS = {
    "captcha": (
        "captcha",
        "капча",
        "капчу",
        "проверочный код",
    ),
    "anti_bot": (
        "anti-bot",
        "antibot",
        "robot",
        "робот",
        "bot detection",
        "challenge",
        "__qrator",
        "qauth",
    ),
    "access_denied": (
        "access denied",
        "access forbidden",
        "forbidden",
        "доступ запрещ",
        "доступ огранич",
        "403 forbidden",
        "http 403",
    ),
    "block": (
        "blocked",
        "блокиров",
        "cloudflare",
        "ddos-guard",
        "защит",
        "security check",
    ),
}


@dataclass(frozen=True)
class SmokeResponse:
    status: int | None
    final_url: str
    content_type: str
    body: bytes
    error: str | None = None

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> SmokeResponse:
    req = Request(url, headers={"User-Agent": UA})

    try:
        with urlopen(req, timeout=timeout) as response:  # nosec B310
            return SmokeResponse(
                status=getattr(response, "status", None),
                final_url=response.geturl(),
                content_type=response.headers.get("Content-Type", ""),
                body=response.read(),
            )
    except HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return SmokeResponse(
            status=exc.code,
            final_url=exc.geturl(),
            content_type=exc.headers.get("Content-Type", "") if exc.headers else "",
            body=body,
            error=f"HTTPError: {exc.reason}",
        )
    except URLError as exc:
        return SmokeResponse(
            status=None,
            final_url=url,
            content_type="",
            body=b"",
            error=f"URLError: {exc.reason}",
        )


def detect_signs(html: str, status: int | None = None) -> dict[str, bool]:
    normalized = html.lower()
    text = _clean_text(html).lower()

    signs = {
        name: any(pattern in normalized or pattern in text for pattern in patterns)
        for name, patterns in SIGN_PATTERNS.items()
    }

    if status in (401, 403, 429):
        signs["block"] = True
    if status == 403:
        signs["access_denied"] = True

    return signs


def count_candidates(html: str) -> dict[str, int]:
    return {
        "legacy_product_cards": len(citilink.CARD_RE.findall(html)),
        "snippet_titles": len(citilink.SNIPPET_TITLE_RE.findall(html)),
        "snippet_prices": len(citilink.SNIPPET_PRICE_RE.findall(html)),
        "product_links": len(PRODUCT_LINK_RE.findall(html)),
        "parsed_cards": len(citilink.parse_cards(html)),
    }


def print_samples(cards: list[dict], limit: int) -> None:
    if not cards:
        print("samples: none")
        return

    print(f"samples shown: {min(limit, len(cards))}")
    for idx, card in enumerate(cards[:limit], start=1):
        print(f"{idx}. {card['price']:.0f} RUB | {card['title']} | {card['url']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test Citilink search parsing diagnostics.")
    parser.add_argument("--url", default=citilink.SEARCH_URL, help="Citilink URL to request")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Request timeout in seconds")
    parser.add_argument("--samples", type=int, default=5, help="Number of parsed card samples to print")
    args = parser.parse_args()

    response = fetch(args.url, timeout=args.timeout)
    html = response.text
    signs = detect_signs(html, response.status)
    counts = count_candidates(html)
    cards = citilink.parse_cards(html)

    print(f"request URL: {args.url}")
    print(f"HTTP status: {response.status if response.status is not None else 'n/a'}")
    print(f"final URL: {response.final_url}")
    print(f"Content-Type: {response.content_type or 'n/a'}")
    print(f"response size: {len(response.body)} bytes")

    if response.error:
        print(f"request error: {response.error}")

    print("signs:")
    for name, value in signs.items():
        print(f"  {name}: {value}")

    print("candidate counts:")
    for name, value in counts.items():
        print(f"  {name}: {value}")

    print_samples(cards, max(0, args.samples))


if __name__ == "__main__":
    main()
