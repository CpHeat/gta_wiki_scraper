from abc import ABC, abstractmethod

class ScrapedData(ABC):
    def __init__(self, name: str, link: str):
        self.name: str = name
        self.link: str = link
        self.image: str = ""


    @abstractmethod
    def get_data(self, is_scraping_needed: bool):
        pass