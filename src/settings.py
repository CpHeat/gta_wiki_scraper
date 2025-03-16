import os

from dotenv import load_dotenv

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')
GLOBAL_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('GLOBAL_CACHE_EXPIRATION_IN_HOURS'))
APARTMENTS_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('APARTMENTS_CACHE_EXPIRATION_IN_HOURS'))
VEHICLES_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('VEHICLES_CACHE_EXPIRATION_IN_HOURS'))
GENERATE_EXCEL_READY_CSV = True if os.getenv('GENERATE_EXCEL_READY_CSV') == "True" else False
EXCEL_HYPERLINK_FORMAT = os.getenv('EXCEL_HYPERLINK_FORMAT')
APARTMENTS_CACHE_EXPIRATION_IN_HOURS = int(os.getenv('APARTMENTS_CACHE_EXPIRATION_IN_HOURS'))

VEHICLES_PAGE_URL = "https://gta.fandom.com/wiki/Vehicles_in_GTA_Online"
VEHICLES_PAGE_OUTPUT = f"{SCRAPED_FOLDER}/vehicles.html"
VEHICLES_CSV_OUTPUT = f"{OUTPUT_FOLDER}/vehicles.csv"
VEHICLES_FIELDNAMES = ("name", "page url", "image url", "category", "type", "body style", "capacity", "speed (km/h)", "speed (mph)", "drivetrain", "modifications")
VEHICLES_MODIFICATIONS_LIST = (
        "armor\\n/strict/",
        ["bodywork", "armor plating", "blades", "rear wheel cover", "roll cage", "spikes"],
        "boost",
        "brakes",
        ["bumpers\\n/strict/", "front bumpers", "rear bumpers"],
        "cam cover",
        "canards",
        "chassis",
        "drift tuning",
        "engine\\n/strict/",
        "engine block",
        "engine covers",
        "exhaust",
        "explosives",
        "fenders",
        "fog lights",
        "grille",
        "headlight covers",
        "hood catches",
        "hood",
        "horn",
        "hsw upgrade",
        "imani",
        ["interior", "dash", "dial design", "doors", "roll cage", "seats", "steering wheel", "trim design"],
        "lights",
        "livery",
        "loss/theft prevention",
        "mirrors",
        "mudguards",
        "name",
        "plateholders",
        "plates",
        "rear panel",
        "rear windshield",
        "respray",
        "roof accessories",
        "roof",
        "sell",
        "side panel",
        "skirts",
        "spoiler",
        "strut braces",
        "sunstrip",
        "suspension",
        "transmission",
        "trim\\n/strict/",
        "trunks",
        "turbo",
        "upgrade",
        "vertical jump",
        ["weapons", "mine"],
        "wheels\\n/strict/",
        "wind deflectors",
        "windows"
    )

APARTMENTS_PAGE_URL = "https://gta.fandom.com/wiki/Apartments"
APARTMENTS_PAGE_OUTPUT = f"{SCRAPED_FOLDER}/apartments.html"
APARTMENTS_CSV_OUTPUT = f"{OUTPUT_FOLDER}/apartments.csv"
APARTMENTS_FIELDNAMES = ("name", "page url", "image url", "category", "style", "garage capacity", "price", "notes")

"""DEBUG VALUES"""
VEHICLES_ITERATION_START = 0
VEHICLES_ITERATION_STOP = None