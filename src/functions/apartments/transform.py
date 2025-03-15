import os
import re

import bs4
from dotenv import load_dotenv

load_dotenv()
SCRAPED_FOLDER = os.getenv('SCRAPED_FOLDER')
LOG_LEVEL = os.getenv('LOG_LEVEL')

def get_image(infos_wrapper: bs4.element.Tag) -> str:
    apartment_image_wrapper = infos_wrapper.find("figure", attrs={'data-source': re.compile(r'^image')})
    return apartment_image_wrapper.find("img").get("src")


def get_style(infos_wrapper: bs4.element.Tag) -> str:
    apartment_style = apartment_style_wrapper = infos_wrapper.find("div", attrs={"data-source": re.compile(r"style", re.I)})
    if apartment_style_wrapper:
        apartment_style = apartment_style_wrapper.find("div", class_="pi-font").getText().split(" (")[0]
        if LOG_LEVEL == "info": print(f"Style is {apartment_style}")
    else:
        if LOG_LEVEL in (["info", "warn"]): print(f"Style is unknown")
    return apartment_style


def get_garage_capacity(infos_wrapper: bs4.element.Tag) -> str:
    garage_capacity_wrapper = infos_wrapper.find("h3", string=lambda text: isinstance(text, str) and "garage capacity" in text.lower())

    if garage_capacity_wrapper:
        garage_capacity = garage_capacity_wrapper.parent.find("div", class_="pi-data-value").getText().split(" ")[0]
        if LOG_LEVEL == "info": print(f"Capacity is {garage_capacity}")
    else:
        garage_capacity = ""
        if LOG_LEVEL in (["info", "warn"]): print(f"Capacity is unknown")
    return garage_capacity