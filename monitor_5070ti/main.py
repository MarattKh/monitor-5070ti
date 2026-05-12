import json
import time
from pathlib import Path

from monitor_5070ti.config.settings import get_settings
from monitor_5070ti.models import ProductOffer


def load_sources() -> list[dict]:
    sources_file = Path(__file__).parent / 'config' / 'sources.json'
    return json.loads(sources_file.read_text(encoding='utf-8'))


def main() -> None:
    settings = get_settings()
    sources = load_sources()
    print(f"Loaded {len(sources)} sources. Interval: {settings.check_interval_sec}s")
    for source in sources:
        offer = ProductOffer(source=source['name'], title=source['product_name'], price=None, in_stock=False, url=source['url'])
        print(f"[{offer.source}] {offer.title}: {'IN STOCK' if offer.in_stock else 'out of stock'}")
    time.sleep(0.1)


if __name__ == '__main__':
    main()
