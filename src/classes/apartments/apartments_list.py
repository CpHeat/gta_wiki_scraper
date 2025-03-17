import re

from src.functions.extract import get_soup
from src.classes.apartments.apartment import Apartment
from src.classes.shared.cache import Cache
from src.classes.shared.scraped_list import ScrapedList
from src.settings import LOG_LEVEL, GENERATE_EXCEL_READY_CSV, EXCEL_HYPERLINK_FORMAT, \
    APARTMENTS_PAGE_OUTPUT, APARTMENTS_CACHE_EXPIRATION_IN_HOURS


class ApartmentsList(ScrapedList):
    """
    A class to represent an items list extracted from a webpage.

    Attributes
    ----------
    page_url: str
        Url of the page to scrape for a list of items.
    output_file: str
        Path to the file containing the scraped page.
    list: dict
        A list of items

    Methods
    -------
    extract_list()
        Extracts the list of items from the url.
    extract_data()
        Extracts individual data for every item in the list.
    get_normalized_price()
        Returns a normalized int price from a string
    """

    def __init__(self, page_url: str, output_file: str):
        """
        Constructs all the necessary attributes for the ApartmentsList object.

        :param page_url: str
            Url of the page to scrape for a list of apartments.
        :param output_file: str
            Path to the local file containing the scraped apartments page.
        """
        super().__init__(page_url, output_file)

    def extract_list(self) -> None:
        """Extracts a list of apartments from a page."""
        apartments = {
            "items": 0,
            "apartments": []
        }

        """Extract every list from the soup"""
        soup = get_soup(APARTMENTS_PAGE_OUTPUT)
        extracted_lists = soup.find_all("table", class_="wikitable")

        """For each list, extract the apartment category from the header"""
        items = 0
        for extracted_list in extracted_lists:
            apartment_header = extracted_list.find(string=re.compile(r"apartment", re.I))
            apartment_category = apartment_header.replace("List of ", "").replace("\\n", "")
            apartments_rows = extracted_list.find_all("tr")

            """For each apartment, extract the data"""
            i = 2
            while i < len(apartments_rows):
                apartment_cells = apartments_rows[i].find_all("td")
                apartment_address = apartment_cells[0].get_text().replace("\\n", "")
                apartment_page = ""
                if apartment_cells[0].find("a"):
                    apartment_page = "https://gta.fandom.com" + apartment_cells[0].find("a").get("href")
                apartment_price = apartment_cells[1].get_text().replace("\\n", "")
                apartment_price = self.get_normalized_price(apartment_price)
                apartment_notes = apartment_cells[2].get_text().replace("\\n", "")
                apartments["apartments"].append({
                    "name": apartment_address,
                    "page url": apartment_page,
                    "category": apartment_category,
                    "price": apartment_price,
                    "notes": apartment_notes,
                })
                i += 1
                items += 1

        """
        Store the number of items and the extracted data in the list
        Check if the previous number of items was different, in which case force rescraping the items pages
        Store the new number of items in the cache
        """
        apartments["items"] = items
        self.list = apartments
        if LOG_LEVEL == "debug": print(f"extracted list: {apartments}")
        Cache.check_for_differences("apartments", self.list['items'])
        Cache.set_list_items("apartments", self.list['items'])

    def extract_data(self) -> None:
        """Extracts individual data for every item in the list."""
        if Cache.is_refresh_needed("apartments_check_timestamp", APARTMENTS_CACHE_EXPIRATION_IN_HOURS):
            print("Apartments cache is outdated, let's go scraping...")
            refresh = True
        else:
            print("Apartments cache is still up to date, working with it...")
            refresh = False

        """
        For each apartment in the list, if it has a page, extract and store the full data
        If it doesn't, use the previous apartment of the same category garage capacity as an extrapolation
        """
        apartments_list = []
        apartments_garage_capacity = {}
        for item in self.list["apartments"]:
            print(f"Processing {item["name"]}...")
            if LOG_LEVEL == "info": print(f"Page: {item["link"]}")

            apartment = Apartment(item["name"], item["page url"], item["price"])

            if item["page url"]:
                apartment.get_item_data(refresh)
            if (not item["page url"] and apartments_garage_capacity.get(item["category"])) or apartment.garage_capacity is None:
                apartment.garage_capacity = apartments_garage_capacity[item["category"]]
            apartments_garage_capacity[item["category"]] = apartment.garage_capacity

            """If asked to generate an excel-compatible csv, modify the links"""
            if GENERATE_EXCEL_READY_CSV:
                page_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + apartment.page_url + "\";\"" + apartment.name + "\")"
                image_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + apartment.image_url + "\";\"" + apartment.name + "\")"
            else:
                page_url = apartment.page_url
                image_url = apartment.image_url

            apartments_list.append({
                "name": item["name"],
                "page url": page_url,
                "image url": image_url,
                "category": item["category"],
                "style": apartment.style,
                "garage capacity": apartment.garage_capacity,
                "price": item["price"],
                "notes": item["notes"]
            })

        """Store the data and update the cache timestamp"""
        self.list["apartments"] = apartments_list
        print("All apartments data extracted!")
        Cache.set_checked_timestamp("apartments_check_timestamp")

    @classmethod
    def get_normalized_price(cls, price: str) -> int:
        """
        Normalizes the price (returns an int from a string)

        :param price: str
            The price string to normalize (strip of symbols and commas)

        :returns: Returns a normalized int price
        """
        return int(price.replace("$", "").replace(",", ""))