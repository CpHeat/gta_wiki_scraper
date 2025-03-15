import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.shared.scraped_data import ScrapedData
from src.functions.apartments.transform import get_image, get_style, get_garage_capacity
from src.functions.shared.extract import normalize_filename, get_page

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')

class Apartment(ScrapedData):
    def __init__(self, name: str, link: str, price):
        super().__init__(name, link)
        self.price: int = price
        self.image: str = ""
        self.style: str = ""
        self.garage_capacity: str = ""


    def get_data(self, is_scraping_needed: bool):
        if self.link:
            normalized_filename = normalize_filename(self.name)
            scraped_page_filename = f"{SCRAPED_FOLDER}/apartments/{normalized_filename}.html"
            if is_scraping_needed:
                get_page(self.link, scraped_page_filename)

            with open(scraped_page_filename, "r") as file:
                soup = BeautifulSoup(file, "html.parser")
            infos_wrapper = soup.find(class_="pi-theme-gta-with-subtitle")

            self.image = get_image(infos_wrapper)
            self.style = get_style(infos_wrapper)
            self.garage_capacity = get_garage_capacity(infos_wrapper)
            if LOG_LEVEL == "info": print(f"{self.name} done!")