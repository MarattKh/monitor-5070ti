from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Mvideo', url='https://www.mvideo.ru/product-list-page?q=rtx%205070%20ti')
