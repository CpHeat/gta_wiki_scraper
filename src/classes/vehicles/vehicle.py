import re

import bs4

from functions.extract import scrape_page, get_normalized_filename, get_soup
from settings import SCRAPED_FOLDER, LOG_LEVEL, VEHICLES_MODIFICATIONS_LIST
from src.classes.shared.scraped_item import ScrapedItem


class Vehicle(ScrapedItem):
    """
    A class to represent a vehicle extracted from a VehiclesList.

    Attributes
    ----------
    name: str
        name of the vehicle.
    page_url: str
        Url of the page to scrape for the vehicle.
    image_url: str
        url for the image of the vehicle.
    category: str
        Category of the vehicle
    type: str
        Type of the vehicle
    body_style: str
        Body Style of the vehicle
    capacity: str
        How many passengers the vehicle can carry
    speed_miles: str
        Speed (in mph) of the vehicle
    speed_km: str
        Speed (in kmh) of the vehicle
    drivetrain: str
        Drivetrain of the vehicle
    modifications: dict
        Dictionary of modifications available for the vehicle

    Methods
    -------
    get_item_data(is_scraping_needed)
        Extracts the apartment data from the item's page.
    get_image_url(data_wrapper)
        Extracts the image url from the data wrapper
    """
    def __init__(self, name: str, page_url: str) -> None:
        """
        Constructs all the necessary attributes for the Vehicle object.

        :param name: str
            Name of the vehicle.
        :param page_url: str
            Url of the page to scrape for the vehicle data.
        """
        super().__init__(name, page_url)
        self.category: str = ""
        self.type: str = ""
        self.body_style: str = ""
        self.capacity: str = ""
        self.speed_miles: str = ""
        self.speed_km: str = ""
        self.drivetrain: str = ""
        self.modifications: dict = {}

    def get_item_data(self, is_scraping_needed: bool):
        """
        Extract the vehicle's data from the vehicle's page.

        :param is_scraping_needed: bool
            Specifies if a scraping of the vehicle's page is needed.
        """
        normalized_filename = get_normalized_filename(self.name)
        scraped_page_filename = f"{SCRAPED_FOLDER}/vehicles/{normalized_filename}.html"
        if is_scraping_needed:
            scrape_page(self.page_url, scraped_page_filename)
        soup = get_soup(scraped_page_filename)
        data_wrapper = soup.find(class_="pi-theme-gta-with-subtitle")

        self.image_url = self.get_image_url(data_wrapper)
        self.category = self.get_category(data_wrapper)
        self.type = self.get_type(data_wrapper)
        self.body_style = self.get_body_style(data_wrapper)
        self.capacity = self.get_capacity(data_wrapper)
        self.speed_km, self.speed_miles = self.get_speed(soup)
        self.drivetrain = self.get_drivetrain(soup)
        self.modifications = self.get_modifications(soup)
        if LOG_LEVEL in ["info", "warn", "debug"]: print(f"{self.name} done!")

    @classmethod
    def get_image_url(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the vehicle's image url from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the vehicle's image url.

        :returns: The vehicle's image url
        """
        vehicle_image_wrapper = data_wrapper.find("figure", attrs={'data-source': re.compile(r'^front_image')})
        return vehicle_image_wrapper.find("img").get("src")

    @classmethod
    def get_category(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the vehicle's category from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the vehicle's category.

        :returns: The vehicle's category
        """
        vehicle_category = vehicle_category_wrapper = data_wrapper.find("div", attrs={
            "data-source": re.compile(r"class", re.I)})
        if vehicle_category_wrapper:
            if vehicle_category_wrapper.find("a"):
                vehicle_category = vehicle_category_wrapper.find("a").getText().split(" (")[0]
            else:
                vehicle_category = vehicle_category_wrapper.find("div", class_="pi-font").getText().split(" (")[0]
            if LOG_LEVEL == "info": print(f"Category is {vehicle_category}")
        else:
            if LOG_LEVEL in ("info", "warn", "debug"): print(f"Category is unknown")
        return vehicle_category

    @classmethod
    def get_type(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the vehicle's type from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the vehicle's type.

        :returns: The vehicle's type
        """
        vehicle_type_wrapper = data_wrapper.find("div", attrs={'data-source': re.compile(r"type", re.I)})
        if vehicle_type_wrapper:
            vehicle_type = vehicle_type_wrapper.find("div", class_="pi-data-value").getText()
            if LOG_LEVEL == "info": print(f"Type is {vehicle_type}")
        else:
            vehicle_type = ""
            if LOG_LEVEL in ("info", "warn", "debug"): print(f"Type is unknown")
        return vehicle_type

    @classmethod
    def get_body_style(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the vehicle's body style from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the vehicle's body style.

        :returns: The vehicle's body style
        """
        vehicle_body_style_wrapper = data_wrapper.find("div", attrs={'data-source': 'body_style'})
        if vehicle_body_style_wrapper:
            vehicle_body_style = vehicle_body_style_wrapper.find("div", class_="pi-data-value").getText()
            if LOG_LEVEL == "info": print(f"Body style is {vehicle_body_style}")
        else:
            vehicle_body_style = ""
            if LOG_LEVEL == "warn": print(f"Body style is unknown")
        return vehicle_body_style

    @classmethod
    def get_capacity(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the vehicle's capacity from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the vehicle's capacity.

        :returns: The vehicle's capacity
        """
        vehicle_capacity_wrapper = data_wrapper.find("div", attrs={'data-source': 'capacity'})
        if vehicle_capacity_wrapper:
            vehicle_capacity = vehicle_capacity_wrapper.find("div", class_="pi-data-value").getText().split(" ")[0]
            if LOG_LEVEL == "info": print(f"Capacity is {vehicle_capacity}")
        else:
            vehicle_capacity = ""
            if LOG_LEVEL == "warn": print(f"Capacity is unknown")
        return vehicle_capacity


    @classmethod
    def get_speed(cls, soup: bs4.element.Tag) -> [str|None]:
        """
        Gets the vehicle's speed from the soup, both in km/h and miles/h.

        :param soup: bs4.element.Tag
            The soup from which to extract the vehicle's speed.

        :returns: The vehicle's speed
        """

        """Search in all th the cell including velocity or top speed"""
        speed_header_cell = next(
            (th for th in soup.find_all("th") if re.search(
                r"\b(?:velocity|top speed)\b", th.get_text(separator=" ", strip=True), re.IGNORECASE))
            , None)

        """If a column exists for the speed, get its data"""
        if speed_header_cell:
            """Get the speed column index"""
            header_row = speed_header_cell.find_parent("tr")
            header_cells = header_row.find_all("th")
            speed_column = header_cells.index(speed_header_cell)
            """Get the speed data row"""
            speed_data_row = header_row.find_next_sibling("tr")
            while speed_data_row and not speed_data_row.find("td"):
                speed_data_row = speed_data_row.find_next_sibling("tr")
            """Check if the data row has a th cell. If it does, diminish the column index by 1 in td cells"""
            speed_data_th = speed_data_row.find_all("th")
            speed_data = speed_data_row.find_all("td")
            if speed_data_th:
                speed = speed_data[speed_column - 1].text.strip("\\n")
            else:
                speed = speed_data[speed_column].text.strip("\\n")
            """Separate the mph and kmh speed"""
            speed = speed.split("/")
            speed_km = speed[0].replace(" ", "")
            speed_miles = speed[1].replace(" ", "")
            if LOG_LEVEL == "info": print(f"Speed is {speed_km}km/h or {speed_miles}Mph")
            return speed_km, speed_miles
        else:
            if LOG_LEVEL in (["info", "warn"]): print(f"Speed is unknown")


    @classmethod
    def get_drivetrain(cls, soup: bs4.element.Tag) -> str|None:
        """
        Gets the vehicle's drivetrain from the soup.
        :param soup: soup from which to extract the vehicle's drivetrain.
        :return: The vehicle's drivetrain
        """
        """Search in all th the cell including drivetrain"""
        drivetrain_header_cell = next(
            (th for th in soup.find_all("th") if re.search(
                r"\b(?:drivetrain)\b", th.get_text(separator=" ", strip=True), re.IGNORECASE))
            , None)

        """If a column exists for the drivetrain, get its data"""
        if drivetrain_header_cell:
            """Get the drivetrain column index"""
            header_row = drivetrain_header_cell.find_parent("tr")
            header_cells = header_row.find_all("th")
            drivetrain_column = header_cells.index(drivetrain_header_cell)
            """Get the drivetrain data row"""
            drivetrain_data_row = header_row.find_next_sibling("tr")
            while drivetrain_data_row and not drivetrain_data_row.find("td"):
                drivetrain_data_row = drivetrain_data_row.find_next_sibling("tr")
            """Check if the data row has a th cell. If it does, diminish the column index by 1 in td cells to compensate"""
            drivetrain_data_th = drivetrain_data_row.find_all("th")
            drivetrain_data = drivetrain_data_row.find_all("td")
            if drivetrain_data_th:
                drivetrain = drivetrain_data[drivetrain_column - 1].text.strip("\\n")
            else:
                drivetrain = drivetrain_data[drivetrain_column].text.strip("\\n")
            if LOG_LEVEL == "info": print(f"Drivetrain is {drivetrain}")
            return drivetrain
        else:
            if LOG_LEVEL == "warn": print(f"Drivetrain is unknown")


    @classmethod
    def get_modifications(cls, soup: bs4.element.Tag):
        """
        Gets the vehicle's modifications counts from the soup.
        :param soup: soup from which to extract the vehicle's modifications counts.
        :return: The vehicle's modifications counts
        """
        modifications = {"total": 0}

        """
        Search for the modification header cell
        if it exists, extract the modifications table and count the rows to establish a theoretical total
        """
        modifications_header = soup.find("th",
                                         string=lambda text: isinstance(text, str) and "modification" in text.lower())
        if modifications_header:
            modifications_count = 0
            modifications_table = modifications_header.find_parent("tbody")
            modifications["theoretical total"] = len(modifications_table.find_all("tr")) - 1

            """For each searchable modification in VEHICLES_MODIFICATIONS_LIST, get its number of rows"""
            for modification_item in VEHICLES_MODIFICATIONS_LIST:
                if type(modification_item) == list:
                    """
                    if modification_item is a list, check for the first term of the list (which is potentially encompassing)
                    if it exists, treat the other terms as subclasses and don't count them in the total
                    if it doesn't exist, treat the other terms as independent
                    """
                    is_subclass = False
                    for index, modification in enumerate(modification_item):
                        modification_count = Vehicle.get_modification(modifications_table, modification)
                        if modification_count > 0:
                            if "/strict/" in modification:
                                modification = modification.replace("\\n/strict/", "")
                            modifications[modification] = modification_count
                            if not is_subclass:
                                modifications_count += modification_count
                            if index == 0:
                                is_subclass = True
                else:
                    modification_count = Vehicle.get_modification(modifications_table, modification_item)
                    """if the item is defined as /strict/ (search for an exact match) get rid of the /strict/ part for the listing"""
                    if "/strict/" in modification_item:
                        modification_item = modification_item.replace("\\n/strict/", "")
                    if modification_count > 0:
                        modifications[modification_item] = modification_count
                        modifications_count += modification_count

            modifications["total"] = modifications_count
            if LOG_LEVEL == "info": print(f"There is a total of {modifications["total"]} modifications available")
            return modifications

    @classmethod
    def get_modification(cls, modifications_table: bs4.element.Tag, modification) -> int:
        """
        Gets the vehicle's modification count from the modifications table.
        :param modifications_table: table from which to extract the vehicle's modification count.
        :param modification: modification name to search for in the table.
        :return: vehicle's modification count.
        """
        """
        if modification is /strict/, search for an exact match and get rid of the /strict/ part for the listing
        else search normally
        """
        if "/strict/" in modification:
            modification = modification.replace("/strict/", "")
            modification_content = modifications_table.find(
                text=re.compile(r"^\s*" + re.escape(modification) + r"\s*$", re.IGNORECASE))
        else:
            modification_content = modifications_table.find(text=re.compile(fr"^\s*{modification}", re.I))
        modification_count = 0
        """if the modification is found in the table, get its rowspan value as count or assume it has only one option"""
        if modification_content:
            modification_cell = modification_content.find_parent("td")
            if modification_content.find_previous_sibling() is None:
                if "rowspan" in modification_cell.attrs:
                    modification_count = int(modification_cell.attrs['rowspan'])
                else:
                    modification_count = 1
        return modification_count