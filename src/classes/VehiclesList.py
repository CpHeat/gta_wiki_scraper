import os
from itertools import islice

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.classes.Cache import Cache
from src.classes.ScrapedList import ScrapedList
from src.classes.Vehicle import Vehicle

load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL')
GENERATE_EXCEL_READY_CSV = os.getenv('GENERATE_EXCEL_READY_CSV')

class VehiclesList(ScrapedList) :
    def __init__(self, scraping_page_url: str):
        super().__init__(scraping_page_url)


    def extract_list(self):
        with open(self.page, "r") as file:
            soup = BeautifulSoup(file, 'html.parser')

        vehicles = soup.find_all("table", class_="wikitable")[-1].find_all("li")
        vehicles_list = []

        # Some vehicles have no link, detect them and scrape them accordingly
        for vehicle in vehicles:
            if vehicle.find("span") and vehicle.find("span").get("data-uncrawlable-url"):
                vehicle_name = vehicle.find("span").get("title").replace(" (page does not exist)", "")
                vehicle_link = ""
            else:
                vehicle_name = vehicle.find("a").get('title', 'No title attribute')
                vehicle_link = "https://gta.fandom.com" + vehicle.find("a").get('href')
            vehicles_list.append({"name": vehicle_name, "link": vehicle_link})

        self.list = vehicles_list
        self.handle_lists_differences()


    def extract_all_vehicles(self):
        if Cache.vehicles_refresh_needed():
            print("Vehicles cache is outdated, let's go scraping...")
            refresh = True
        else:
            print("Vehicles cache is still up to date, working with it...")
            refresh = False
        for index, vehicle in enumerate(islice(self.list, 0, None)):
            print(f"Processing {index}: {vehicle['name']}...")
            if LOG_LEVEL == "info": print(f"Page: {vehicle["link"]}")

            vehicle = Vehicle(index, vehicle["name"], vehicle["link"])
            vehicle.get_data(scraping_needed=refresh)
            if GENERATE_EXCEL_READY_CSV:
                link = "=[BATCH_DELETE_THIS]HYPERLINK(\"" + vehicle.link + "\";\"" + vehicle.name + "\")"
                image_url = "=[BATCH_DELETE_THIS]HYPERLINK(\"" + vehicle.image + "\";\"" + vehicle.name + "\")"
            else:
                link = vehicle.link
                image_url = vehicle.image
            self.list[index] = {
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

        print("All vehicles done!")
        Cache.set_vehicles_check_timestamp(force_refresh=False)
        Cache.set_vehicles_list(self.list)


    def handle_lists_differences(self):
        if len(Cache.get_vehicles_list()) != len(self.list):
            Cache.set_vehicles_check_timestamp(force_refresh=True)
        else:
            return False