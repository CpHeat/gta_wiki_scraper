import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.apartments.apartment import Apartment
from src.classes.shared.cache import Cache
from src.classes.shared.scraped_list import ScrapedList
from src.settings import APARTMENTS_PAGE_OUTPUT

load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL')
GENERATE_EXCEL_READY_CSV = True if os.getenv('GENERATE_EXCEL_READY_CSV') == "True" else False
EXCEL_HYPERLINK_FORMAT = os.getenv('EXCEL_HYPERLINK_FORMAT')
APARTMENTS_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('APARTMENTS_CACHE_EXPIRATION_IN_HOURS'))

class ApartmentsList(ScrapedList):
    def __init__(self):
        super().__init__()


    """ Extract the full list of every apartment in the game, by type
    """
    def extract_list(self):
        apartments_list = {
            "items": 0,
            "apartments": []
        }
        with open(APARTMENTS_PAGE_OUTPUT, "r") as file:
            soup = BeautifulSoup(file, 'html.parser')

        extracted_lists = soup.find_all("table", class_="wikitable")
        items=0
        for extracted_list in extracted_lists:
            apartment_header = extracted_list.find(string = re.compile(r"apartment", re.I))
            apartment_header = apartment_header.replace("List of ", "").replace("\\n", "")
            apartments_rows = extracted_list.find_all("tr")
            i=2
            while i < len(apartments_rows):
                apartment_cells = apartments_rows[i].find_all("td")
                apartment_address = apartment_cells[0].get_text().replace("\\n", "")
                apartment_page = ""
                if apartment_cells[0].find("a"):
                    apartment_page = "https://gta.fandom.com" + apartment_cells[0].find("a").get("href")
                apartment_price = apartment_cells[1].get_text().replace("\\n", "")
                apartment_price = self.normalize_price(apartment_price)
                apartment_notes = apartment_cells[2].get_text().replace("\\n", "")
                apartments_list["apartments"].append({
                    "name": apartment_address,
                    "link": apartment_page,
                    "category": apartment_header,
                    "price": apartment_price,
                    "notes": apartment_notes,
                })
                i+=1
                items+=1
        apartments_list["items"] = items
        self.list = apartments_list
        if LOG_LEVEL == "debug": print(f"extracted list: {apartments_list}")
        self.check_for_differences()
        Cache.set_list_items("apartments", self.list['items'])


    def extract_data(self):
        if Cache.is_refresh_needed("apartments_check_timestamp", APARTMENTS_CACHE_EXPIRATION_IN_HOURS):
            print("Apartments cache is outdated, let's go scraping...")
            refresh = True
        else:
            print("Apartments cache is still up to date, working with it...")
            refresh = False
        apartments_list = []
        for apartment_data in self.list["apartments"]:
            print(f"Processing {apartment_data["name"]}...")
            if LOG_LEVEL == "info": print(f"Page: {apartment_data["link"]}")
            apartment = Apartment(apartment_data["name"], apartment_data["link"], apartment_data["price"])
            apartment.get_data(refresh)
            if GENERATE_EXCEL_READY_CSV:
                link = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + apartment.link + "\";\"" + apartment.name + "\")"
                image_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + apartment.image + "\";\"" + apartment.name + "\")"
            else:
                link = apartment.link
                image_url = apartment.image
            apartments_list.append({
                "name": apartment_data["name"],
                "link": link,
                "image url": image_url,
                "category": apartment_data["category"],
                "style": apartment.style,
                "garage capacity": apartment.garage_capacity,
                "price": apartment_data["price"],
                "notes": apartment_data["notes"]
            })
        self.list["apartments"] = apartments_list
        print("All apartments data extracted!")
        Cache.set_checked_timestamp("apartments_check_timestamp", force_refresh=False)


    def check_for_differences(self):
        if Cache.get_list_items("apartments") != self.list["items"]:
            if LOG_LEVEL == "debug": print(f"List is different than the cached one, refresh it")
            Cache.set_checked_timestamp("apartments_check_timestamp", force_refresh=True)
        else:
            return False


    @classmethod
    def normalize_price(cls, price: str):
        return price.replace("$", "").replace(",", "")