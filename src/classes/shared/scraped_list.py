from abc import ABC, abstractmethod

class ScrapedList(ABC):
    def __init__(self):
        self.list: dict = {}


    @abstractmethod
    def extract_list(self):
        pass


    @abstractmethod
    def extract_data(self):
        pass


    @abstractmethod
    def check_for_differences(self):
        pass