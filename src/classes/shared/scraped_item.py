from abc import ABC, abstractmethod

import bs4


class ScrapedItem(ABC):
    """
    A class to represent an item extracted from a ScrapedList.

    Attributes
    ----------
    name: str
        name of the item.
    page_url: str
        Url of the page to scrape for the item.
    image_url: str
        url for the image of the item.

    Methods
    -------
    get_item_data(is_scraping_needed)
        Extracts the item data from the item's page.
    get_image_url(data_wrapper)
        Extracts the image url from the data wrapper
    """
    def __init__(self, name: str, page_url: str) -> None:
        """
        Constructs all the necessary attributes for the ScrapedItem object.

        :param name: str
            Name of the item
        :param page_url: str
            Url of the page to scrape for the item data.
        """
        self.name: str = name
        self.page_url: str = page_url
        self.image_url: str = ""

    @abstractmethod
    def get_item_data(self, is_scraping_needed: bool):
        """
        Extracts the item data from the item's page.

        :param is_scraping_needed: bool
            Specifies if a scraping of the item's page is needed.
        """
        pass

    @classmethod
    @abstractmethod
    def get_image_url(cls, data_wrapper: bs4.element.Tag) -> str:
        """
        Gets the image url from the data wrapper.

        :param data_wrapper: bs4.element.Tag
            The html data wrapper from which to extract the image url.

        :returns: The image url
        """
        pass