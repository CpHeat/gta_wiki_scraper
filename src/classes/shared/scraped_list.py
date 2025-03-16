from abc import ABC, abstractmethod


class ScrapedList(ABC):
    """
    A class to represent an items list extracted from a webpage.

    Attributes
    ----------
    page_url: str
        Url of the page to scrape for a list of items.
    output_file: str
        Path to the local file containing the scraped page.
    list: dict
        A list of items

    Methods
    -------
    extract_list()
        Extracts the list of items from the url.
    extract_data()
        Extracts individual data for every item in the list that has its own url.
    """
    def __init__(self, page_url: str, output_file: str) -> None:
        """
        Constructs all the necessary attributes for the ScrapedList object.

        :param page_url: str
            Url of the page to scrape for a list of items.
        :param output_file: str
            Path to the local file containing the scraped items page.
        """
        self.page_url: str = page_url
        self.output_file: str = output_file
        self.list: dict = {}

    @abstractmethod
    def extract_list(self) -> None:
        """Extracts a list of items from a page."""
        pass

    @abstractmethod
    def extract_data(self) -> None:
        """Extracts individual data for every item in the list that has its own url, then updates the list with the data obtained."""
        pass