from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Wildberries', url='https://www.wildberries.ru/catalog/0/search.aspx?search=rtx%205070%20ti')
