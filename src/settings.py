import os

from dotenv import load_dotenv

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')

VEHICLES_PAGE_URL = "https://gta.fandom.com/wiki/Vehicles_in_GTA_Online"
VEHICLES_PAGE_OUTPUT = f"{SCRAPED_FOLDER}/vehicles.html"
VEHICLES_CSV_OUTPUT = f"{OUTPUT_FOLDER}/vehicles.csv"
VEHICLES_FIELDNAMES = ("name", "link", "image url", "category", "type", "body style", "capacity", "speed (km/h)", "speed (mph)", "drivetrain", "modifications")

APARTMENTS_PAGE_URL = "https://gta.fandom.com/wiki/Apartments"
APARTMENTS_PAGE_OUTPUT = f"{SCRAPED_FOLDER}/apartments.html"
APARTMENTS_CSV_OUTPUT = f"{OUTPUT_FOLDER}/apartments.csv"
APARTMENTS_FIELDNAMES = ("name", "link", "image url", "category", "style", "garage capacity", "price", "notes")

# DEBUG VALUES
VEHICLES_ITERATION_START = 0
VEHICLES_ITERATION_STOP = None