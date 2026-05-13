from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Cdek Shopping', url='https://cdek.shopping/search/?q=rtx%205070%20ti')
