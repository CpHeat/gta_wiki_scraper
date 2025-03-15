import os

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.shared.scraped_data import ScrapedData
from src.functions.shared.extract import normalize_filename, get_page
from src.functions.vehicles.transform import get_image, get_category, get_type, get_body_style, get_capacity, get_speed, get_drivetrain, get_modifications

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')

class Vehicle(ScrapedData):
    def __init__(self, name: str, link: str):
        super().__init__(name, link)
        self.category: str = ""
        self.type: str = ""
        self.body_style: str = ""
        self.capacity: str = ""
        self.speed_miles: str = ""
        self.speed_km: str = ""
        self.drivetrain: str = ""
        self.modifications = {}


    def get_data(self, is_scraping_needed: bool):
        if self.link:
            normalized_filename = normalize_filename(self.name)
            scraped_page_filename = f"{SCRAPED_FOLDER}/vehicles/{normalized_filename}.html"
            if is_scraping_needed:
                get_page(self.link, scraped_page_filename)

            with open(scraped_page_filename, "r") as file:
                soup = BeautifulSoup(file, "html.parser")
            infos_wrapper = soup.find(class_="pi-theme-gta-with-subtitle")

            self.image = get_image(infos_wrapper)
            self.category = get_category(infos_wrapper)
            self.type = get_type(infos_wrapper)
            self.body_style = get_body_style(infos_wrapper)
            self.capacity = get_capacity(infos_wrapper)
            self.speed_km, self.speed_miles = get_speed(soup)
            self.drivetrain = get_drivetrain(soup)
            self.modifications = get_modifications(soup)
            if LOG_LEVEL in ["info", "warn", "debug"]: print(f"{self.name} done!")