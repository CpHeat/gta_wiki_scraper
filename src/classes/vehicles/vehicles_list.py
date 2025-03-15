import os
from itertools import islice

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.shared.cache import Cache
from src.classes.shared.scraped_list import ScrapedList
from src.settings import VEHICLES_PAGE_OUTPUT, VEHICLES_ITERATION_START, VEHICLES_ITERATION_STOP
from src.classes.vehicles.vehicle import Vehicle

load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL')
GENERATE_EXCEL_READY_CSV = True if os.getenv('GENERATE_EXCEL_READY_CSV') == "True" else False
EXCEL_HYPERLINK_FORMAT = os.getenv('EXCEL_HYPERLINK_FORMAT')
VEHICLES_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('VEHICLES_CACHE_EXPIRATION_IN_HOURS'))

class VehiclesList(ScrapedList):
    def __init__(self):
        super().__init__()


    def extract_list(self):
        with open(VEHICLES_PAGE_OUTPUT, "r") as file:
            soup = BeautifulSoup(file, 'html.parser')

        vehicles = soup.find_all("table", class_="wikitable")[-1].find_all("li")
        vehicles_list = {
            "items": 0,
            "vehicles": []
        }

        # Some vehicles have no link, detect them and scrape them accordingly
        items=0
        for vehicle in vehicles:
            if vehicle.find("span") and vehicle.find("span").get("data-uncrawlable-url"):
                vehicle_name = vehicle.find("span").get("title").replace(" (page does not exist)", "")
                vehicle_link = ""
            else:
                vehicle_name = vehicle.find("a").get('title', 'No title attribute')
                vehicle_link = "https://gta.fandom.com" + vehicle.find("a").get('href')
            items += 1
            vehicles_list["vehicles"].append({"name": vehicle_name, "link": vehicle_link})
        vehicles_list["items"] = items
        self.list = vehicles_list
        self.check_for_differences()
        Cache.set_list_items("vehicles", self.list['items'])


    def extract_data(self):
        if Cache.is_refresh_needed("vehicles_check_timestamp", VEHICLES_CACHE_EXPIRATION_IN_HOURS):
            print("Vehicles cache is outdated, let's go scraping...")
            refresh = True
        else:
            print("Vehicles cache is still up to date, working with it...")
            refresh = False
        for index, vehicle in enumerate(islice(self.list["vehicles"], VEHICLES_ITERATION_START, VEHICLES_ITERATION_STOP)):
            print(f"Processing {index}: {vehicle['name']}...")
            if LOG_LEVEL == "info": print(f"Page: {vehicle["link"]}")

            vehicle = Vehicle(vehicle["name"], vehicle["link"])
            vehicle.get_data(refresh)
            print("gec", GENERATE_EXCEL_READY_CSV)
            if GENERATE_EXCEL_READY_CSV:
                print("generate excel ready")
                link = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + vehicle.link + "\";\"" + vehicle.name + "\")"
                image_url = "=[BATCH_DELETE_THIS]" + EXCEL_HYPERLINK_FORMAT + "(\"" + vehicle.image + "\";\"" + vehicle.name + "\")"
            else:
                print("generate not excel ready")
                link = vehicle.link
                image_url = vehicle.image
            self.list["vehicles"][index] = {
                "name": vehicle.name,
                "link": link,
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


    def check_for_differences(self):
        if Cache.get_list_items("vehicles") != self.list["items"]:
            if LOG_LEVEL == "debug": print(f"List is different than the cached one, refresh it")
            Cache.set_checked_timestamp("vehicles_check_timestamp", force_refresh=True)
        else:
            return False