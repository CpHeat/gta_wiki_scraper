import os
from pathlib import Path
import csv
import datetime
from itertools import islice
import pandas
import requests
import unicodedata
import re
import bs4
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook
from dotenv import load_dotenv

load_dotenv()
CACHE_EXPIRATION_IN_HOURS = float(os.getenv('CACHE_EXPIRATION_IN_HOURS'))
LOG_LEVEL = os.getenv('LOG_LEVEL')

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


# Analyze the page and extract the data from the vehicles table
def extract_vehicles_table(vehicles_page:str):
    with open(vehicles_page, "r") as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.find_all("table", class_="wikitable")


# Analyze the vehicles table and extract the name and link for every model
def extract_vehicles_list(vehicles_table:str):
    soup = BeautifulSoup(vehicles_table, 'html.parser')
    vehicles = soup.find_all("li")
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
    return vehicles_list


def get_vehicle_image(vehicle_infos:bs4.element.Tag):
    vehicle_image_wrapper = vehicle_infos.find("figure", attrs={'data-source': re.compile(r'^front_image')})
    return vehicle_image_wrapper.find("img").get("src")


def get_vehicle_class(vehicle_infos):
    vehicle_class = vehicle_class_wrapper = vehicle_infos.find("div", attrs={'data-source': 'class'})
    if vehicle_class_wrapper:
        if vehicle_class_wrapper.find("a"):
            vehicle_class = vehicle_class_wrapper.find("a").getText().split(" (")[0]
        else:
            vehicle_class = vehicle_class_wrapper.find("div", class_="pi-font").getText().split(" (")[0]
        if LOG_LEVEL == "info" : print(f"Class is {vehicle_class}")
    else:
        if LOG_LEVEL in (["info", "warn"]): print(f"Class is unknown")
    return vehicle_class


def get_vehicle_type(vehicle_infos):
    vehicle_type_wrapper = vehicle_infos.find("div", attrs={'data-source': 'type'})
    if vehicle_type_wrapper:
        vehicle_type = vehicle_type_wrapper.find("div", class_="pi-data-value").getText()
        if LOG_LEVEL == "info": print(f"Type is {vehicle_type}")
    else:
        vehicle_type = ""
        if LOG_LEVEL in (["info", "warn"]): print(f"Type is unknown")
    return vehicle_type


def get_vehicle_body_style(vehicle_infos):
    vehicle_body_style_wrapper = vehicle_infos.find("div", attrs={'data-source': 'body_style'})
    if vehicle_body_style_wrapper:
        vehicle_body_style = vehicle_body_style_wrapper.find("div", class_="pi-data-value").getText()
        if LOG_LEVEL == "info": print(f"Body style is {vehicle_body_style}")
    else:
        vehicle_body_style = ""
        if LOG_LEVEL in (["info", "warn"]): print(f"Body style is unknown")
    return vehicle_body_style


def get_vehicle_capacity(vehicle_infos):
    vehicle_capacity_wrapper = vehicle_infos.find("div", attrs={'data-source': 'capacity'})
    if vehicle_capacity_wrapper:
        vehicle_capacity = vehicle_capacity_wrapper.find("div", class_="pi-data-value").getText().split(" ")[0]
        if LOG_LEVEL == "info" : print(f"Capacity is {vehicle_capacity}")
    else:
        vehicle_capacity = ""
        if LOG_LEVEL in (["info", "warn"]): print(f"Capacity is unknown")
    return vehicle_capacity


def get_vehicle_drivetrain(soup:bs4.BeautifulSoup):
    drivetrain_header_cell = next((th for th in soup.find_all("th") if re.search(r"\b(?:drivetrain)\b", th.get_text(separator=" ", strip=True), re.IGNORECASE)), None)
    if drivetrain_header_cell:
        header_row = drivetrain_header_cell.find_parent("tr")
        if header_row:
            header_cells = header_row.find_all("th")
            drivetrain_column = header_cells.index(drivetrain_header_cell)
            vehicle_drivetrain_infos_row = header_row.find_next_sibling("tr")
            while vehicle_drivetrain_infos_row and not vehicle_drivetrain_infos_row.find("td"):
                vehicle_drivetrain_infos_row = vehicle_drivetrain_infos_row.find_next_sibling("tr")
            vehicle_drivetrain_infos_th = vehicle_drivetrain_infos_row.find_all("th")
            vehicle_drivetrain_infos = vehicle_drivetrain_infos_row.find_all("td")
            if vehicle_drivetrain_infos_th:
                vehicle_drivetrain = vehicle_drivetrain_infos[drivetrain_column - 1].text.strip("\\n")
            else:
                vehicle_drivetrain = vehicle_drivetrain_infos[drivetrain_column].text.strip("\\n")
            if LOG_LEVEL == "info": print(f"Drivetrain is {vehicle_drivetrain}")
            return vehicle_drivetrain
    else:
        if LOG_LEVEL in (["info", "warn"]): print(f"Drivetrain is unknown")
        return ""


def get_vehicle_speed(soup:bs4.BeautifulSoup):
    speed_header_cell = next((th for th in soup.find_all("th") if re.search(r"\b(?:velocity|top speed)\b", th.get_text(separator=" ", strip=True), re.IGNORECASE)), None)
    if speed_header_cell:
        header_row = speed_header_cell.find_parent("tr")
        if header_row:
            header_cells = header_row.find_all("th")
            speed_column = header_cells.index(speed_header_cell)
            vehicle_speed_infos_row = header_row.find_next_sibling("tr")
            while vehicle_speed_infos_row and not vehicle_speed_infos_row.find("td"):
                vehicle_speed_infos_row = vehicle_speed_infos_row.find_next_sibling("tr")
            vehicle_speed_infos_th = vehicle_speed_infos_row.find_all("th")
            vehicle_speed_infos = vehicle_speed_infos_row.find_all("td")
            if vehicle_speed_infos_th:
                vehicle_speed = vehicle_speed_infos[speed_column - 1].text.strip("\\n")
            else:
                vehicle_speed = vehicle_speed_infos[speed_column].text.strip("\\n")
            if LOG_LEVEL == "info" : print(f"Speed is {vehicle_speed}")
            return vehicle_speed
    else:
        if LOG_LEVEL in (["info", "warn"]): print(f"Speed is unknown")
        return ""


# Get the number of modifications available
def get_modifications(soup:bs4.BeautifulSoup, modifications_list:list):
    modifications = {"total": 0}
    modification_header = soup.find("th", string=lambda text: "Modification" in text if text else False)
    if modification_header:
        modifications_count = 0
        table = modification_header.find_parent("tbody")

        if table:
            for modification in modifications_list:
                modification_cell = table.find("td", string=lambda text: modification in text if text else False, attrs={"rowspan": True})
                if modification_cell:
                    modification_count = int(modification_cell.get("rowspan"))
                    modifications_count += modification_count
                    modifications[modification.strip("\\n")] = modification_count

        modifications["total"] = modifications_count
        if LOG_LEVEL == "info" : print(f"There is a total of {modifications["total"]} modifications available")
        return modifications


# Extract the infos for a vehicle
def extract_vehicle_infos(vehicle_page:str, modifications_list:list):
    with open(vehicle_page, "r") as file:
        soup = BeautifulSoup(file, "html.parser")
        vehicle_infos = soup.find(class_ = "pi-theme-gta-with-subtitle")
        vehicle_image = get_vehicle_image(vehicle_infos)
        vehicle_class = get_vehicle_class(vehicle_infos)
        vehicle_type = get_vehicle_type(vehicle_infos)
        vehicle_body_style = get_vehicle_body_style(vehicle_infos)
        vehicle_capacity = get_vehicle_capacity(vehicle_infos)
        vehicle_speed = get_vehicle_speed(soup)
        vehicle_drivetrain = get_vehicle_drivetrain(soup)
        vehicle_modifications = get_modifications(soup, modifications_list)

        return {
            "image": vehicle_image,
            "class": vehicle_class,
            "type": vehicle_type,
            "body-style": vehicle_body_style,
            "speed": vehicle_speed,
            "drivetrain": vehicle_drivetrain,
            "capacity": vehicle_capacity,
            "modifications": vehicle_modifications
        }


# Save infos in a csv file
def load_vehicles_infos(vehicles_list:list, vehicle_csv_output:str):
    with open(vehicle_csv_output, "w", newline='', encoding='utf-8') as output:
        fieldnames = ["name", "link", "image", "class", "type", "body-style", "capacity", "modifications"]
        writer = csv.DictWriter(output, fieldnames = fieldnames, delimiter = ",")
        writer.writeheader()
        for vehicle_data in vehicles_list:
            writer.writerow(vehicle_data)
    print(f"CSV file created : {vehicle_csv_output}")


# Generate a xlsx file with hyperlinks
def generate_xlsx(csv_file:str, output_xlsx:str):
    # load CSV
    df = pandas.read_csv(csv_file)

    # Create Excel file
    wb = Workbook()
    ws = wb.active

    # Add headers
    for col_idx, col_name in enumerate(df.columns, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    # Insert data with hyperlinks
    for row_idx, row in df.iterrows():
        for col_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=row_idx + 2, column=col_idx, value=value)

            # Check if value is hyperlink
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                cell.hyperlink = value
                cell.value = "Link"  # Texte raccourci affiché
                cell.style = "Hyperlink"

    # Save Excel file
    wb.save(output_xlsx)
    print(f"Excel file created : {output_xlsx}")


def get_cache(cache_file:str, CACHE_EXPIRATION_IN_HOURS:float):
    f = open(cache_file, "r")
    cache_timestamp = float(f.read())
    current_timestamp = datetime.datetime.now().timestamp()

    if (cache_timestamp + (CACHE_EXPIRATION_IN_HOURS * 3600)) <= float(current_timestamp):
        print("Cache outdated, let's go scraping...")
        return True
    else:
        print("Cache is still recent, working with local files...")
        return False


def set_cache(cache_file:str):
    current_timestamp = str(datetime.datetime.now().timestamp())
    f = open(cache_file, "w")
    f.write(current_timestamp)
    f.close()


def main():
    scraped_folder = "../scraped"
    output_folder = "../output"
    vehicles_page_url = "https://gta.fandom.com/wiki/Vehicles_in_GTA_Online"
    Path(scraped_folder).mkdir(parents=True, exist_ok=True)
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    vehicles_page_output = f"{scraped_folder}/gta_vehicles_page.html"
    vehicle_csv_output = f"{output_folder}/vehicles.csv"
    vehicles_xlsx_output = f"{output_folder}/vehicles.xlsx"
    cache_file = "cache.txt"
    refresh_cache = get_cache(cache_file, CACHE_EXPIRATION_IN_HOURS)

    modifications_list = [
        "Armor Plating\\n",
        "Blades\\n",
        "Cam Cover\\n",
        "Dash\\n",
        "Doors\\n",
        "Drift Tuning\\n",
        "Engine Block\\n",
        "Exhaust\\n",
        "Exhausts\\n",
        "Explosives\\n",
        "Fenders\\n",
        "Fog Lights\\n",
        "Front Bumpers\\n",
        "Headlight Covers\\n",
        "Hood Catches\\n",
        "Hoods\\n",
        "Livery\\n",
        "Mirrors\\n",
        "Mudguards\\n",
        "Plateholders\\n",
        "Rear Bumpers\\n",
        "Roll Cages\\n",
        "Roofs\\n",
        "Seats\\n",
        "Skirts\\n",
        "Spikes\\n",
        "Spoilers\\n",
        "Steering Wheels\\n",
        "Strut Braces\\n",
        "Trunks\\n",
        "Vertical Jump\\n",
        "Weapons\\n",
    ]

    # If outdated, get content of the main vehicles page on GTA Wiki
    if refresh_cache:
        get_page(vehicles_page_url, vehicles_page_output)

    # Analyze the page and extract the vehicles list
    vehicles_table = str(extract_vehicles_table(vehicles_page_output))
    vehicles_list = extract_vehicles_list(vehicles_table)

    # Go through the list and get each page. processing_start allow to start at a specific index if needed
    processing_start = 0
    processing_stop = None
    for index, vehicle in enumerate(islice(vehicles_list, processing_start, processing_stop)):
        print(f"Processing {index}: {vehicle['name']}...")
        if LOG_LEVEL == "info": print(f"Page: {vehicle["link"]}")

        # If the vehicle has a page get it and extract the infos
        if vehicle["link"]:
            normalized_filename = normalize_filename(vehicle["name"])
            scraped_page_filename = f"{scraped_folder}/{normalized_filename}.html"
            if refresh_cache:
                get_page(vehicle["link"], scraped_page_filename)

            vehicle_infos = extract_vehicle_infos(scraped_page_filename, modifications_list)
            vehicle["image"] = vehicle_infos["image"]
            vehicle["class"] = vehicle_infos["class"]
            vehicle["type"] = vehicle_infos["type"]
            vehicle["body-style"] = vehicle_infos["body-style"]
            vehicle["capacity"] = vehicle_infos["capacity"]
            vehicle["modifications"] = vehicle_infos["modifications"]
            if LOG_LEVEL == "info" : print(f"{vehicle["name"]} done!")

    load_vehicles_infos(vehicles_list, vehicle_csv_output)
    generate_xlsx(vehicle_csv_output, vehicles_xlsx_output)
    set_cache(cache_file)


if __name__ == "__main__":
    main()