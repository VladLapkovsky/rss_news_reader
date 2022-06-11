"""This module provides a class to save and read news in/from a file.

News articles are saved in a file in JSON format.
News in a file has the following structure:

[

{date: [news, news, news]},

{date: [news, news, news]},

]

Date has "%Y%m%d" format.
"""

import functools
import itertools
import json
import operator
import os
from datetime import datetime

from rss_parser.logger import LOGGER


class NewsStorage:
    """A class that saves and reads a news in/from a file."""

    def __init__(self, news_limit: int = None, file_name: str = "stored_news.txt"):
        """Provide "NewsStorage" initialization.

        Save file in the "rss_parser" folder in JSON format.

        Args:
            news_limit (int): determine the limit of the number of news, which will be read from the file
            file_name (str): name of file to save news
        """
        self._news_limit = int(news_limit) if news_limit is not None else news_limit

        self.file_name = file_name
        self.path = os.getcwd() + os.path.sep + self.file_name

    def save_news_to_file(self, news_to_save: list):
        """Save news in the file.

        Group news articles by it's date and save them in a file in JSON format.

        Args:
            news_to_save (list): list of news, news in dict format
        """
        LOGGER.info("saving news to the file...")
        news_to_save = self._group_news_by_date(news_to_save)
        with open(self.path, "w") as file_to_write:
            json.dump(news_to_save, file_to_write, indent=4)

    def get_news_from_file(self, news_date: str = None) -> list:
        """Read news form the file.

        If the "news_date" is not specified, all news from the file will be returned.

        If the "news_date" is specified, all news in a given date will be returned.
        Date should match to "20210102" format (day and month from 01 to 09 with 0).

        "self._news_limit" limits the number of returned news. If it's None, all news will be returned.
        If it's greater than total number of news, all news will be returned.

        Args:
            news_date (str): the date per which news articles are got

        Returns:
            list of news from a file

        Raises:
            ValueError: if storage file is not exist
        """
        LOGGER.warning("getting news from the file...")
        if not os.path.exists(self.path):
            raise ValueError("error: news storage file doesn't exist, run program with the 'source' argument first")
        with open(self.path, "r") as file_to_read:
            data_from_file = json.load(file_to_read)

        # data_from_file -> list of dicts (key - date, value - news in this date)
        news_from_file = self._get_news_by_date(
            data_from_file,
            news_date,
        ) if news_date is not None else self._get_all_news(data_from_file)

        len_of_news_from_file = len(news_from_file)
        if self._news_limit and len_of_news_from_file < self._news_limit:
            self._news_limit = len_of_news_from_file
            LOGGER.info(
                "the limit is greater than news number, the total number of news will be %s", len_of_news_from_file,
            )
        return news_from_file[:self._news_limit] if self._news_limit is not None else news_from_file

    def _get_news_by_date(self, data_from_file: list, news_date: str) -> list:
        try:
            return next(news[news_date] for news in data_from_file if news.get(news_date))
        except StopIteration as error:
            raise ValueError("error: no news for the specified date") from error

    def _get_all_news(self, data_from_file: list) -> list:
        all_news = []
        for news in data_from_file:
            all_news.extend(functools.reduce(operator.iconcat, news.values(), []))
        return all_news

    def _get_reformatted_date(self, date_to_reformat: str) -> str:
        input_pattern = "%Y-%m-%d %H:%M:%S"
        output_pattern = "%Y%m%d"
        return datetime.strptime(date_to_reformat, input_pattern).strftime(output_pattern)

    def _group_news_by_date(self, news_to_safe: list) -> list:
        news_sorted_by_date = sorted(news_to_safe, key=lambda news: news["date"])
        groups = itertools.groupby(news_sorted_by_date, key=lambda news: self._get_reformatted_date(news["date"]))
        return [{key: list(group)} for key, group in groups]
