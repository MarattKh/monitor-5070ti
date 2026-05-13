from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Yandex Market', url='https://market.yandex.ru/search?text=rtx%205070%20ti')
