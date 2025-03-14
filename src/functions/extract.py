import re

import requests
import unicodedata


MODIFICATIONS_LIST = (
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

# Get page content and save it locally
def get_page(url:str, output_file:str):
    print(f"Scraping {url}...")
    page = requests.get(url)
    f = open(output_file, "w")
    f.write(str(page.content))
    f.close()
    print(f"Scraping done!")


# Normalize filename
def normalize_filename(filename:str):
    filename = unicodedata.normalize('NFKC', filename)
    filename = re.sub(r'[^\w\s-]', '', filename.lower())
    return re.sub(r'[-\s]+', '-', filename).strip('-_')