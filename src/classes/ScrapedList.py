class ScrapedList:
    def __init__(self, scraping_page_url: str):
        self.page: str = scraping_page_url
        self.list: list = []

    def extract_lit(self):
        pass