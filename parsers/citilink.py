from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Ситилинк', url='https://www.citilink.ru/search/?text=rtx%205070%20ti')
