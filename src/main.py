import os
from pathlib import Path

from dotenv import load_dotenv

from src.settings import VEHICLES_PAGE_URL, VEHICLES_PAGE_OUTPUT, VEHICLES_CSV_OUTPUT, VEHICLES_FIELDNAMES, \
    APARTMENTS_PAGE_URL, APARTMENTS_PAGE_OUTPUT, APARTMENTS_CSV_OUTPUT, APARTMENTS_FIELDNAMES
from src.classes.apartments.apartments_list import ApartmentsList
from src.classes.shared.cache import Cache
from src.classes.vehicles.vehicles_list import VehiclesList
from src.functions.shared.extract import get_page
from src.functions.shared.load import load_data_to_csv

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')
GLOBAL_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('GLOBAL_CACHE_EXPIRATION_IN_HOURS'))
APARTMENTS_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('APARTMENTS_CACHE_EXPIRATION_IN_HOURS'))
VEHICLES_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('VEHICLES_CACHE_EXPIRATION_IN_HOURS'))

def main():
    Path(SCRAPED_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(SCRAPED_FOLDER + "/vehicles").mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER + "/vehicles").mkdir(parents=True, exist_ok=True)
    Path(SCRAPED_FOLDER + "/apartments").mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER + "/apartments").mkdir(parents=True, exist_ok=True)

    # If outdated, get content of the main vehicles page on GTA Wiki
    if Cache.is_refresh_needed("global_check_timestamp", GLOBAL_CACHE_EXPIRATION_IN_HOURS):
        print("Global cache outdated, let's go scraping...")
        get_page(VEHICLES_PAGE_URL, VEHICLES_PAGE_OUTPUT)
        get_page(APARTMENTS_PAGE_URL, APARTMENTS_PAGE_OUTPUT)
        Cache.set_checked_timestamp("global_check_timestamp", False)
    else:
        print("Global cache still up to date, let's work with it")

    # Analyze the page and extract the vehicles list
    vehicles_list = VehiclesList()
    vehicles_list.extract_list()
    vehicles_list.extract_data()

    # Analyze the page and extract the apartments list
    apartments_list = ApartmentsList()
    apartments_list.extract_list()
    apartments_list.extract_data()

    if LOG_LEVEL == "debug": print(vehicles_list.list)
    if LOG_LEVEL == "debug": print(apartments_list.list)
    load_data_to_csv(vehicles_list.list["vehicles"], VEHICLES_CSV_OUTPUT, VEHICLES_FIELDNAMES)
    load_data_to_csv(apartments_list.list["apartments"], APARTMENTS_CSV_OUTPUT, APARTMENTS_FIELDNAMES)


if __name__ == "__main__":
    main()