from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Regard', url='https://www.regard.ru/catalog/tovar/search?search=rtx+5070+ti')
