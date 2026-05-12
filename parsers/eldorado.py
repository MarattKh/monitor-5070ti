from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Eldorado', url='https://www.eldorado.ru/search/catalog.php?q=rtx%205070%20ti')
