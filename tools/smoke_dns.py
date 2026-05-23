from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from parsers import dns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", action="store_true", help="Use Playwright browser mode for DNS")
    args = parser.parse_args()

    result = dns.parse_offers_with_status(browser_mode=args.browser)
    offers = result.get("offers", [])

    print(f"blocked: {result.get('blocked')}")
    print(f"block_reason: {result.get('block_reason')}")
    print(f"errors: {result.get('errors')}")
    print(f"warnings: {result.get('warnings')}")
    print(f"offers count: {len(offers)}")

    for idx, offer in enumerate(offers[:5], start=1):
        print(f"{idx}. {offer.price:.0f} {offer.currency} | {offer.title} | {offer.url}")


if __name__ == "__main__":
    main()
