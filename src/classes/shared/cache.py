import shelve
from datetime import datetime

from src.settings import LOG_LEVEL


class Cache:
    """Contains all the cache methods."""
    def __init__(self):
        pass

    @classmethod
    def set_checked_timestamp(cls, timestamp_name: str, force_refresh: bool = False) -> None:
        """
        Sets the cache timestamp for a checked list
        :param timestamp_name: str
            The list for which to set the timestamp in the cache
        :param force_refresh: bool
            Force reinitialization of the timestamp
        """
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            if force_refresh:
                cache[timestamp_name] = 0
            else:
                cache[timestamp_name] = str(datetime.now().timestamp())

    @classmethod
    def is_refresh_needed(cls, timestamp_name: str, cache_expiration: int) -> bool:
        """
        Checks if a rescraping is needed

        :param timestamp_name: str
            The cache timestamp to check
        :param cache_expiration: int
            The cache duration to check against
        """
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
    def reset_timestamps(cls) -> None:
        """Resets the check timestamps"""
        cls.set_checked_timestamp("global_check_timestamp", True)
        cls.set_checked_timestamp("vehicles_check_timestamp", True)
        cls.set_checked_timestamp("apartments_check_timestamp", True)

    @classmethod
    def set_list_items(cls, list_name: str, items: int) -> None:
        """
        Sets the number of items for a list in the cache

        :param list_name: str
            The list for which to get the items count
        :param items: int
            The number of items to set in cache
        """
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            cache[list_name] = items

    @classmethod
    def get_list_items(cls, list_name:str) -> int:
        """
        Gets the number of items for a list in the cache

        :param list_name: str
            The list for which to get the items count
        """
        with shelve.open("cache", flag='c', protocol=None, writeback=False) as cache:
            try:
                return cache[list_name]
            except KeyError:
                cache[list_name] = 0
                return 0

    @classmethod
    def check_for_differences(cls, checked_item: str, items_count: int) -> None:
        """
        check if the newly extracted list has the same number of items than the one stored in cache.
        If not, overrides the refresh timer to trigger a full scraping again.

        :param checked_item: str
            The item count to go check in the cache.
        :param items_count: int
            The item count to compare it with.
        """
        if cls.get_list_items(checked_item) != items_count:
            if LOG_LEVEL == "debug": print(f"List is different than the cached one, refresh it")
            Cache.set_checked_timestamp("apartments_check_timestamp", force_refresh=True)