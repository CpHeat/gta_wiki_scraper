import re

import bs4
import unicodedata

import requests
from bs4 import BeautifulSoup


def scrape_page(url:str, output_file:str) -> None:
    """
    Scrapes a page url and saves it locally.

    :param url: url of the page to scrape.
    :param output_file: str: filename for the local file to save.
    """
    print(f"Scraping {url}...")
    page = requests.get(url)
    f = open(output_file, "w")
    f.write(str(page.content))
    f.close()
    print(f"Scraping done!")

def get_normalized_filename(name: str) -> str:
    """
    Get a name and return a normalized filename

    :param name: name to normalize

    :return: normalized filename
    """
    filename = unicodedata.normalize('NFKC', name)
    filename = re.sub(r'[^\w\s-]', '', filename.lower())
    return re.sub(r'[-\s]+', '-', filename).strip('-_')

def get_soup(local_file: str) -> bs4.element.Tag:
    """
    Get soup from a local scraped file

    :param local_file: local scraped file from which to extract soup

    :return: soup
    """
    with open(local_file, "r") as file:
        return BeautifulSoup(file, 'html.parser')