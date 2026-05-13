from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Computeruniverse', url='https://www.computeruniverse.net/en/search?query=rtx%205070%20ti')
