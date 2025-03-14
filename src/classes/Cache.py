import os
import shelve
from datetime import datetime

from dotenv import load_dotenv


load_dotenv()
GLOBAL_CACHE_EXPIRATION_IN_HOURS = float(os.getenv('GLOBAL_CACHE_EXPIRATION_IN_HOURS'))
VEHICLES_CACHE_EXPIRATION_IN_HOURS = float(os.getenv('VEHICLES_CACHE_EXPIRATION_IN_HOURS'))

class Cache:
    def __init__(self):
        pass


    @classmethod
    def set_global_check_timestamp(cls):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            cache["global_check_timestamp"] = str(datetime.now().timestamp())


    @classmethod
    def set_vehicles_check_timestamp(cls, force_refresh):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            if force_refresh:
                cache["vehicles_check_timestamp"] = 0
            else:
                cache["vehicles_check_timestamp"] = str(datetime.now().timestamp())


    @classmethod
    def set_vehicles_list(cls, vehicles_list):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            cache["vehicles_list"] = vehicles_list


    @classmethod
    def get_vehicles_list(cls):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            try:
                return cache["vehicles_list"]
            except KeyError:
                cache["vehicles_list"] = []
                return []


    @classmethod
    def global_refresh_needed(cls) -> bool:
        with shelve.open("cache") as cache:
            try:
                if (float(cache["global_check_timestamp"]) + GLOBAL_CACHE_EXPIRATION_IN_HOURS * 3600) < datetime.now().timestamp():
                    return True
                else:
                    return False
            except KeyError:
                cache["global_check_timestamp"] = 0
                return True


    @classmethod
    def vehicles_refresh_needed(cls) -> bool:
        with shelve.open("cache") as cache:
            try:
                if (float(cache["vehicles_check_timestamp"]) + VEHICLES_CACHE_EXPIRATION_IN_HOURS * 3600) < datetime.now().timestamp():
                    return True
                else:
                    return False
            except KeyError:
                cache["vehicles_check_timestamp"] = 0
                return True