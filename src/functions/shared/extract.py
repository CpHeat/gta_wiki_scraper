import re
import unicodedata

import requests

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