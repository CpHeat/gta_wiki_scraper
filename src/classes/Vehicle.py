import os
import re

import bs4.element
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.Cache import Cache
from src.functions.extract import normalize_filename, get_page, MODIFICATIONS_LIST

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')

class Vehicle:
    def __init__(self, id: int, name: str, link: str):
        self.id: int = id
        self.name: str = name
        self.link: str = link
        self.soup: bs4.element.Tag | None = None
        self.infos_wrapper: bs4.element.Tag | None = None
        self.image: str = ""
        self.category: str = ""
        self.type: str = ""
        self.body_style: str = ""
        self.capacity: str = ""
        self.speed_miles: str = ""
        self.speed_km: str = ""
        self.drivetrain: str = ""
        self.modifications: dict[str: int] = {}


    def get_data(self, scraping_needed: bool):
        if self.link:
            normalized_filename = normalize_filename(self.name)
            scraped_page_filename = f"{SCRAPED_FOLDER}/{normalized_filename}.html"
            if scraping_needed:
                get_page(self.link, scraped_page_filename)
                Cache.set_vehicles_check_timestamp(False)
            self.soup = self.get_soup(scraped_page_filename)
            self.infos_wrapper = self.soup.find(class_="pi-theme-gta-with-subtitle")
            self.get_image()
            self.get_category()
            self.get_type()
            self.get_body_style()
            self.get_capacity()
            self.get_speed()
            self.get_drivetrain()
            self.get_modifications()
            if LOG_LEVEL == "info": print(f"{self.name} done!")


    @classmethod
    def get_soup(cls, vehicle_page: str) -> bs4.element.Tag:
        with open(vehicle_page, "r") as file:
            return BeautifulSoup(file, "html.parser")


    def get_image(self):
        vehicle_image_wrapper = self.infos_wrapper.find("figure", attrs={'data-source': re.compile(r'^front_image')})
        self.image = vehicle_image_wrapper.find("img").get("src")


    def get_category(self):
        vehicle_category = vehicle_category_wrapper = self.infos_wrapper.find("div", attrs={"data-source": re.compile(r"class", re.I)})
        if vehicle_category_wrapper:
            if vehicle_category_wrapper.find("a"):
                vehicle_category = vehicle_category_wrapper.find("a").getText().split(" (")[0]
            else:
                vehicle_category = vehicle_category_wrapper.find("div", class_="pi-font").getText().split(" (")[0]
            if LOG_LEVEL == "info": print(f"Category is {vehicle_category}")
        else:
            if LOG_LEVEL in (["info", "warn"]): print(f"Class is unknown")
        self.category = vehicle_category


    def get_type(self):
        vehicle_type_wrapper = self.infos_wrapper.find("div", attrs={'data-source': re.compile(r"type", re.I)})
        if vehicle_type_wrapper:
            vehicle_type = vehicle_type_wrapper.find("div", class_="pi-data-value").getText()
            if LOG_LEVEL == "info": print(f"Type is {vehicle_type}")
        else:
            vehicle_type = ""
            if LOG_LEVEL in (["info", "warn"]): print(f"Type is unknown")
        self.type = vehicle_type


    def get_body_style(self):
        vehicle_body_style_wrapper = self.infos_wrapper.find("div", attrs={'data-source': 'body_style'})
        if vehicle_body_style_wrapper:
            vehicle_body_style = vehicle_body_style_wrapper.find("div", class_="pi-data-value").getText()
            if LOG_LEVEL == "info": print(f"Body style is {vehicle_body_style}")
        else:
            vehicle_body_style = ""
            if LOG_LEVEL in (["info", "warn"]): print(f"Body style is unknown")
        self.body_style = vehicle_body_style


    def get_capacity(self):
        vehicle_capacity_wrapper = self.infos_wrapper.find("div", attrs={'data-source': 'capacity'})
        if vehicle_capacity_wrapper:
            vehicle_capacity = vehicle_capacity_wrapper.find("div", class_="pi-data-value").getText().split(" ")[0]
            if LOG_LEVEL == "info": print(f"Capacity is {vehicle_capacity}")
        else:
            vehicle_capacity = ""
            if LOG_LEVEL in (["info", "warn"]): print(f"Capacity is unknown")
        self.capacity = vehicle_capacity


    def get_speed(self):
        speed_header_cell = next((th for th in self.soup.find_all("th") if re.search(r"\b(?:velocity|top speed)\b",
                                                                                th.get_text(separator=" ", strip=True),
                                                                                re.IGNORECASE)), None)

        if speed_header_cell:
            header_row = speed_header_cell.find_parent("tr")
            if header_row:
                header_cells = header_row.find_all("th")
                speed_column = header_cells.index(speed_header_cell)
                vehicle_speed_infos_row = header_row.find_next_sibling("tr")
                while vehicle_speed_infos_row and not vehicle_speed_infos_row.find("td"):
                    vehicle_speed_infos_row = vehicle_speed_infos_row.find_next_sibling("tr")
                vehicle_speed_infos_th = vehicle_speed_infos_row.find_all("th")
                vehicle_speed_infos = vehicle_speed_infos_row.find_all("td")
                if vehicle_speed_infos_th:
                    vehicle_speed = vehicle_speed_infos[speed_column - 1].text.strip("\\n")
                else:
                    vehicle_speed = vehicle_speed_infos[speed_column].text.strip("\\n")

                vehicle_speed = vehicle_speed.split("/")
                self.speed_km = vehicle_speed[0].replace(" ", "")
                self.speed_miles = vehicle_speed[1].replace(" ", "")
                if LOG_LEVEL == "info": print(f"Speed is {self.speed_km}km/h or {self.speed_miles}Mph")
        else:
            if LOG_LEVEL in (["info", "warn"]): print(f"Speed is unknown")


    def get_drivetrain(self):
        drivetrain_header_cell = next((th for th in self.soup.find_all("th") if re.search(r"\b(?:drivetrain)\b",
                                                                                     th.get_text(separator=" ",
                                                                                                 strip=True),
                                                                                     re.IGNORECASE)), None)
        if drivetrain_header_cell:
            header_row = drivetrain_header_cell.find_parent("tr")
            if header_row:
                header_cells = header_row.find_all("th")
                drivetrain_column = header_cells.index(drivetrain_header_cell)
                vehicle_drivetrain_infos_row = header_row.find_next_sibling("tr")
                while vehicle_drivetrain_infos_row and not vehicle_drivetrain_infos_row.find("td"):
                    vehicle_drivetrain_infos_row = vehicle_drivetrain_infos_row.find_next_sibling("tr")
                vehicle_drivetrain_infos_th = vehicle_drivetrain_infos_row.find_all("th")
                vehicle_drivetrain_infos = vehicle_drivetrain_infos_row.find_all("td")
                if vehicle_drivetrain_infos_th:
                    vehicle_drivetrain = vehicle_drivetrain_infos[drivetrain_column - 1].text.strip("\\n")
                else:
                    vehicle_drivetrain = vehicle_drivetrain_infos[drivetrain_column].text.strip("\\n")
                if LOG_LEVEL == "info": print(f"Drivetrain is {vehicle_drivetrain}")
                self.drivetrain = vehicle_drivetrain
        else:
            if LOG_LEVEL in (["info", "warn"]): print(f"Drivetrain is unknown")


    def get_modifications(self):
        modifications = {"total": 0}

        modifications_header = self.soup.find("th", string=lambda text: isinstance(text, str) and "modification" in text.lower())
        if modifications_header:
            modifications_count = 0
            modifications_table = modifications_header.find_parent("tbody")
            modifications["Theoretical total"] = len(modifications_table.find_all("tr"))-1

            if modifications_table:
                for modification_item in MODIFICATIONS_LIST:

                    if type(modification_item) == list:
                        """
                        check for the first term of the list (which is englobing)
                        if it exists, treat the other terms as subclasses and don't count them in the total
                        if it doesn't exist, treat the other terms as independent
                        """
                        is_subclass = False
                        for index, modification in enumerate(modification_item):
                            modification_count = self.get_modification(modifications_table, modification)
                            if modification_count > 0:
                                modifications[modification] = modification_count
                                if not is_subclass:
                                    modifications_count += modification_count
                                if index == 0:
                                    is_subclass = True
                    else:
                        modification_count = self.get_modification(modifications_table, modification_item)
                        if modification_count > 0:
                            modifications[modification_item] = modification_count
                            modifications_count += modification_count

            modifications["total"] = modifications_count
            if LOG_LEVEL == "info": print(f"There is a total of {modifications["total"]} modifications available")
            self.modifications = modifications


    def get_modification(self, modifications_table:bs4.element.Tag, modification):
        if "/strict/" in modification:
            modification = modification.replace("/strict/", "")
            modification_content = modifications_table.find(text=re.compile(r"^\s*" + re.escape(modification) + r"\s*$", re.IGNORECASE))
        else:
            modification_content = modifications_table.find(text=re.compile(fr"^\s*{modification}", re.I))
        modification_count = 0

        if modification_content:
            modification_cell = modification_content.find_parent("td")
            if modification_content.find_previous_sibling() is None:
                if "rowspan" in modification_cell.attrs:
                    modification_count = int(modification_cell.attrs['rowspan'])
                else:
                    modification_count = 1
        return modification_count