from pathlib import Path

from classes.vehicles.vehicles_list import VehiclesList
from functions.extract import scrape_page
from src.settings import SCRAPED_FOLDER, OUTPUT_FOLDER, \
    VEHICLES_PAGE_URL, VEHICLES_PAGE_OUTPUT, VEHICLES_CSV_OUTPUT, VEHICLES_FIELDNAMES, \
    APARTMENTS_PAGE_URL, APARTMENTS_PAGE_OUTPUT, APARTMENTS_CSV_OUTPUT, APARTMENTS_FIELDNAMES, \
    GLOBAL_CACHE_EXPIRATION_IN_HOURS, LOG_LEVEL
from src.classes.apartments.apartments_list import ApartmentsList
from src.classes.shared.cache import Cache
from src.functions.load import load_data_to_csv


def main() -> None:
    """Check and create paths"""
    Path(SCRAPED_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(SCRAPED_FOLDER + "/vehicles").mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER + "/vehicles").mkdir(parents=True, exist_ok=True)
    Path(SCRAPED_FOLDER + "/apartments").mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER + "/apartments").mkdir(parents=True, exist_ok=True)

    """If outdated, get content of the main vehicles page on GTA Wiki"""
    if Cache.is_refresh_needed("global_check_timestamp", GLOBAL_CACHE_EXPIRATION_IN_HOURS):
        print("Global cache outdated, let's go scraping...")
        scrape_page(VEHICLES_PAGE_URL, VEHICLES_PAGE_OUTPUT)
        scrape_page(APARTMENTS_PAGE_URL, APARTMENTS_PAGE_OUTPUT)
        Cache.set_checked_timestamp("global_check_timestamp", False)
    else:
        print("Global cache still up to date, let's work with it")

    """Analyze the page and extract the vehicles data"""
    vehicles = VehiclesList(VEHICLES_PAGE_URL, VEHICLES_PAGE_OUTPUT)
    vehicles.extract_list()
    vehicles.extract_data()

    """Analyze the page and extract the apartments data"""
    apartments_list = ApartmentsList(APARTMENTS_PAGE_URL, APARTMENTS_PAGE_OUTPUT)
    apartments_list.extract_list()
    apartments_list.extract_data()

    """Save data in csv files"""
    if LOG_LEVEL == "debug": print(vehicles.list)
    if LOG_LEVEL == "debug": print(apartments_list.list)
    load_data_to_csv(vehicles.list["vehicles"], VEHICLES_CSV_OUTPUT, VEHICLES_FIELDNAMES)
    load_data_to_csv(apartments_list.list["apartments"], APARTMENTS_CSV_OUTPUT, APARTMENTS_FIELDNAMES)


if __name__ == "__main__":
    main()
