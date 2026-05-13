from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Megamarket', url='https://megamarket.ru/catalog/?q=rtx%205070%20ti')
