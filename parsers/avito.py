from parsers.common import scrape_search_page


def parse_offers():
    return scrape_search_page(source='Avito', url='https://www.avito.ru/rossiya/tovary_dlya_kompyutera?q=rtx+5070+ti')
