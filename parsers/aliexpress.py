from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Aliexpress', url='https://aliexpress.ru/wholesale?SearchText=rtx+5070+ti')
