from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Dns', url='https://www.dns-shop.ru/search/?q=rtx+5070+ti')
