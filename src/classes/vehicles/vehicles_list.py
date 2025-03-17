from itertools import islice

from src.functions.extract import get_soup
from src.classes.shared.cache import Cache
from src.classes.shared.scraped_list import ScrapedList
from src.settings import LOG_LEVEL, GENERATE_EXCEL_READY_CSV, EXCEL_HYPERLINK_FORMAT, \
    VEHICLES_PAGE_OUTPUT, VEHICLES_ITERATION_START, VEHICLES_ITERATION_STOP, VEHICLES_CACHE_EXPIRATION_IN_HOURS
from src.classes.vehicles.vehicle import Vehicle


class VehiclesList(ScrapedList):
    """
    A class to represent a vehicles list extracted from a webpage.

    Attributes
    ----------
    page_url: str
        Url of the page to scrape for a list of vehicles.
    output_file: str
        Path to the local file containing the scraped page.
    list: dict
        A list of vehicles

    Methods
    -------
    extract_list()
        Extracts the list of vehicles from the url.
    extract_data()
        Extracts individual data for every vehicle in the list that has its own url.
    """
    def __init__(self, page_url: str, output_file: str) -> None:
        """
        Constructs all the necessary attributes for the VehiclesList object.

        :param page_url: str
            Url of the page to scrape for a list of vehicles.
        :param output_file: str
            Path to the local file containing the scraped vehicles page.
        """
        super().__init__(page_url, output_file)

    def extract_list(self) -> None:
        """Extracts a list of vehicles from a page."""
        vehicles = {
            "items": 0,
            "vehicles": []
        }

        """Extract the vehicles list from the soup"""
        soup = get_soup(VEHICLES_PAGE_OUTPUT)
        vehicles_list = soup.find_all("table", class_="wikitable")[-1].find_all("li")

        """Some vehicles have no link, detect them and scrape them accordingly"""
        items=0
        for vehicle in vehicles_list:
            if vehicle.find("span") and vehicle.find("span").get("data-uncrawlable-url"):
                vehicle_name = vehicle.find("span").get("title").replace(" (page does not exist)", "")
                vehicle_page_url = ""
            else:
                vehicle_name = vehicle.find("a").get('title', 'No title attribute')
                vehicle_page_url = "https://gta.fandom.com" + vehicle.find("a").get('href')
            items += 1
            vehicles["vehicles"].append({"name": vehicle_name, "page url": vehicle_page_url})
        vehicles["items"] = items
        self.list = vehicles
        Cache.check_for_differences("vehicles", self.list['items'])
        Cache.set_list_items("vehicles", self.list['items'])


    def extract_data(self) -> None:
        """Extracts individual data for every vehicle in the list."""
        if Cache.is_refresh_needed("vehicles_check_timestamp", VEHICLES_CACHE_EXPIRATION_IN_HOURS):
            print("Vehicles cache is outdated, let's go scraping...")
            refresh = True
        else:
            print("Vehicles cache is still up to date, working with it...")
            refresh = False

        """For each vehicle in the list that has a page, extract and store the full data"""
        for index, item in enumerate(islice(self.list["vehicles"], VEHICLES_ITERATION_START, VEHICLES_ITERATION_STOP)):
            print(f"Processing {index}: {item['name']}...")
            if LOG_LEVEL == "info": print(f"Page: {item["link"]}")

            vehicle = Vehicle(item["name"], item["page url"])
            if item["page url"]:
                vehicle.get_item_data(refresh)

            """If asked to generate an excel-compatible csv, modify the links"""
            if GENERATE_EXCEL_READY_CSV:
                page_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + vehicle.page_url + "\";\"" + vehicle.name + "\")"
                image_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + vehicle.image + "\";\"" + vehicle.name + "\")"
            else:
                page_url = vehicle.page_url
                image_url = vehicle.image_url

            self.list["vehicles"][index] = {
                "name": vehicle.name,
                "page url": page_url,
                "image url": image_url,
                "category": vehicle.category,
                "type": vehicle.type,
                "body style": vehicle.body_style,
                "capacity": vehicle.capacity,
                "speed (km/h)": vehicle.speed_km,
                "speed (mph)": vehicle.speed_miles,
                "drivetrain": vehicle.drivetrain,
                "modifications": vehicle.modifications
            }
        print("All vehicles data extracted!")
        Cache.set_checked_timestamp("vehicles_check_timestamp", force_refresh=False)