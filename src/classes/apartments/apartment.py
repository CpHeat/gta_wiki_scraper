import re

import bs4

from src.settings import SCRAPED_FOLDER, LOG_LEVEL
from src.classes.shared.scraped_item import ScrapedItem
from src.functions.extract import get_normalized_filename, get_soup, scrape_page


class Apartment(ScrapedItem):
    """
    A class to represent an apartment extracted from an ApartmentsList.

    Attributes
    ----------
    name: str
        name of the apartment.
    page_url: str
        Url of the page to scrape for the apartment.
    image_url: str
        url for the image of the apartment.
    price: int
        The price of the apartment.
    style: str
        The apartment's style
    garage_capacity: int
        The number of vehicles the apartment's garage can contain.

    Methods
    -------
    get_item_data(is_scraping_needed)
        Extracts the apartment data from the item's page.
    get_image_url(data_wrapper)
        Extracts the image url from the data wrapper
    get_style(data_wrapper)
        Gets the apartment style string from the data wrapper.
    get_garage_capacity(data_wrapper)
        Gets the apartment garage capacity from the data wrapper.
    """
    def __init__(self, name: str, page_url: str, price: int):
        """
        Constructs all the necessary attributes for the Apartment object.

        :param name: str
            Name of the apartment.
        :param page_url: str
            Url of the page to scrape for the apartment data.
        :param price: int
            The price of the apartment.
        """
        super().__init__(name, page_url)
        self.price: int = price
        self.style: str = ""
        self.garage_capacity: str = ""

    def get_item_data(self, is_scraping_needed: bool):
        """
        Extract the apartment's data from the apartment's page.

        :param is_scraping_needed: bool
            Specifies if a scraping of the apartment's page is needed.
        """
        normalized_filename = get_normalized_filename(self.name)
        scraped_page_filename = f"{SCRAPED_FOLDER}/apartments/{normalized_filename}.html"
        if is_scraping_needed:
            scrape_page(self.page_url, scraped_page_filename)
        soup = get_soup(scraped_page_filename)
        data_wrapper = soup.find(class_="pi-theme-gta-with-subtitle")

        self.image_url = self.get_image_url(data_wrapper)
        self.style = self.get_style(data_wrapper)
        self.garage_capacity = self.get_garage_capacity(data_wrapper)
        if LOG_LEVEL == "info": print(f"{self.name} done!")

    @classmethod
    def get_image_url(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the apartment's image url from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the apartment's image url.

        :returns: The apartment's image url
        """
        apartment_image_wrapper = data_wrapper.find("figure", attrs={'data-source': re.compile(r'^image')})
        return apartment_image_wrapper.find("img").get("src")

    @classmethod
    def get_style(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the apartment style string from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the apartment style string.

        :returns: The apartment style string
        """
        apartment_style = apartment_style_wrapper = data_wrapper.find("div", attrs={
            "data-source": re.compile(r"style", re.I)})
        if apartment_style_wrapper:
            apartment_style = apartment_style_wrapper.find("div", class_="pi-font").getText().split(" (")[0]
            if LOG_LEVEL == "info": print(f"Style is {apartment_style}")
        else:
            if LOG_LEVEL in (["info", "warn"]): print(f"Style is unknown")
        return apartment_style

    @classmethod
    def get_garage_capacity(cls, data_wrapper: bs4.element.Tag) -> int|None:
        """
        Gets the apartment garage capacity from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the apartment garage capacity style string.

        :returns: The apartment garage capacity or None if not available
        """
        garage_capacity_wrapper = data_wrapper.find("h3", string=lambda text: isinstance(text, str) and "garage capacity" in text.lower())

        if garage_capacity_wrapper:
            garage_capacity = garage_capacity_wrapper.parent.find("div", class_="pi-data-value").getText().split(" ")[0]
            if LOG_LEVEL == "info": print(f"Capacity is {garage_capacity}")
        else:
            garage_capacity = None
            if LOG_LEVEL in (["info", "warn"]): print(f"Capacity is unknown")
        return garage_capacity