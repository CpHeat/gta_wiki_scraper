import shelve
from datetime import datetime

class Cache:
    def __init__(self):
        pass


    @classmethod
    def set_checked_timestamp(cls, timestamp_name:str, force_refresh: bool):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            if force_refresh:
                cache[timestamp_name] = 0
            else:
                cache[timestamp_name] = str(datetime.now().timestamp())


    @classmethod
    def set_list_items(cls, list_name: str, items: int):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            cache[list_name] = items


    @classmethod
    def get_list_items(cls, list_name:str):
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            try:
                return cache[list_name]
            except KeyError:
                cache[list_name] = 0
                return 0


    @classmethod
    def is_refresh_needed(cls, timestamp_name:str, cache_expiration: int) -> bool:
        with shelve.open("cache") as cache:
            try:
                if (float(cache[timestamp_name]) + cache_expiration * 3600) < datetime.now().timestamp():
                    return True
                else:
                    return False
            except KeyError:
                cache[timestamp_name] = 0
                return True


    @classmethod
    def reset_timestamps(cls):
        cls.set_checked_timestamp("global_check_timestamp", True)
        cls.set_checked_timestamp("vehicles_check_timestamp", True)
        cls.set_checked_timestamp("apartments_check_timestamp", True)