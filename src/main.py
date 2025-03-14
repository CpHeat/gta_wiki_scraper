import os
import csv
import re
from pathlib import Path

import pandas
from dotenv import load_dotenv
from openpyxl.workbook import Workbook

from src.classes.Cache import Cache
from src.classes.VehiclesList import VehiclesList
from src.functions.extract import get_page


load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL')
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')

# Save infos in a csv file
def load_vehicles_infos(vehicles_list:list, vehicle_csv_output:str):
    with open(vehicle_csv_output, "w", newline='', encoding='utf-8') as output:
        fieldnames = ["name", "link", "image url", "category", "type", "body style", "capacity", "speed (km/h)", "speed (mph)", "drivetrain", "modifications"]
        writer = csv.DictWriter(output, fieldnames = fieldnames, delimiter = ",")
        writer.writeheader()
        for vehicle_data in vehicles_list:
            writer.writerow(vehicle_data)
    print(f"CSV file created : {vehicle_csv_output}")



def main():
    vehicles_page_url = "https://gta.fandom.com/wiki/Vehicles_in_GTA_Online"
    Path(SCRAPED_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    vehicles_page_output = f"{SCRAPED_FOLDER}/gta_vehicles_page.html"
    vehicle_csv_output = f"{OUTPUT_FOLDER}/vehicles.csv"
    vehicles_xlsx_output = f"{OUTPUT_FOLDER}/vehicles.xlsx"

    # If outdated, get content of the main vehicles page on GTA Wiki
    if Cache.global_refresh_needed():
        print("Global cache outdated, let's go scraping...")
        get_page(vehicles_page_url, vehicles_page_output)
        Cache.set_global_check_timestamp()
    else:
        print("Global cache still up to date, let's work with it")

    # Analyze the page and extract the vehicles list
    vehicles_list = VehiclesList(vehicles_page_output)
    vehicles_list.extract_list()
    vehicles_list.extract_all_vehicles()

    print(vehicles_list.list)

    load_vehicles_infos(vehicles_list.list, vehicle_csv_output)


if __name__ == "__main__":
    main()