"""This module provides main logic of the command-line RSS reader.

Classes:
    ParserManager: manages the process of creating and displaying news.
    ParserNewsFormer: manages the processing of news.
    ParserNewsHandler: manages the process of serializing and printing news.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from dateutil import parser as dateutil_parser

from rss_parser.logger import LOGGER
from rss_parser.news_handler import FileConverter, Printer
from rss_parser.news_object import NewsObject
from rss_parser.news_separator import separate_news
from rss_parser.news_storage import NewsStorage
from rss_parser.web_parser.web_parser import WebParser


class ParserNewsHandler:
    """Provide the process of serializing and printing rss-news."""

    def __init__(self):
        """Provide default data format to handle."""
        self.data_format = "LIST"

    def serialize_news(self, news_to_serialize: list) -> list:
        """Serialize news. The serialization format depends on "self.data_format".

        Expect "LIST" or "JSON" data format.

        Args:
            news_to_serialize (list): an iterable object with news to serialize

        Returns:
            serialized or non serialized news
        """
        news_to_serialize = news_to_serialize[:]
        if self.data_format == "JSON":
            LOGGER.info("serializing news to %s format...", self.data_format)
            for number, news_container in enumerate(news_to_serialize):
                news_to_serialize[number] = json.dumps(news_container, indent=4)
        return news_to_serialize

    def process_news(self, news_to_process, news_handler):
        """Process news depending on the "self.data_format".

        The class in the "news_handler" argument must be able to handle "news_to_process".

        Args:
            news_to_process: an iterable object with news to process
            news_handler: a class with "process_news" method and "object_to_handle" and "data_format" arguments
        """
        news_handler().process_news(object_to_handle=news_to_process, data_format=self.data_format)

    def register_data_format_to_process(self, format_to_process: str):
        """Change "self.data_format" if "format_to_process" is not None.

        Args:
            format_to_process (str): format to register
        """
        if format_to_process is not None:
            self.data_format = format_to_process.upper()


class ParserNewsFormer:
    """Provide logic of forming rss-news."""

    def __init__(self, rss_page, news_limit: int = None, news_date: str = None):
        """Provide "ParserNewsFormer" initialization.

        Args:
            rss_page: a BS4 xml-page is expected
            news_limit (int): limits the number of news to be processed. If None, all news on page will be processed
            news_date (str): specify the date per which news articles are got
        """
        LOGGER.info("preparing to form news...")
        self._rss_page = rss_page
        self._news_limit = news_limit

        self._title = self._rss_page.title.string
        self._news_date = news_date

    def form_news(self) -> list:
        """Run forming news logic.

        "executor_pool" use "submit" from "ThreadPoolExecutor" to create a future representing the given call.
        The given call creates class instances.

        "executor_pool" has the following structure: [class_instances, class_instances, ...]

        The class of these instances is given by the first argument.
        This class should provide the "form_news" method and contain the "news_container" argument.
        The other arguments in the "submit" are sent to the "__init__" of this class.

        The number of instances is equal to the len of "news_list".
        "news_list" is formed by the "self._form_news_list" method.
        The "self._form_news_list" method gets all rss-articles from "item" tag.
        If "self._news_date" is not None, list of articles contains news only for the specified date.

        After that the "result" method is used for every future representing to return the result of the call that
        the future represents. Every result calls the "form_news" method and saves formed news to the "news_storage".

        Returns:
            a list of formed news
        """
        news_storage = []
        news_list = self._form_news_list(self._news_date)
        LOGGER.info("start forming news...")
        with ThreadPoolExecutor() as executor:
            executor_pool = [
                executor.submit(
                    NewsObject,
                    self._title,
                    certain_rss_news,
                    WebParser,
                    "lxml",
                ) for certain_rss_news in news_list
            ]

            for executor_result in executor_pool:
                LOGGER.info(separate_news())
                LOGGER.warning("***forming news number %s***\n", executor_pool.index(executor_result) + 1)

                news_object = executor_result.result()
                news_object.form_news()
                news_storage.append(news_object.news_container)
        LOGGER.info(separate_news())
        LOGGER.info("forming news is completed...")
        return news_storage

    def _form_news_limit(self, list_of_news: list) -> int:
        news_on_page = len(list_of_news)
        news_limit = int(self._news_limit) if self._news_limit else self._news_limit
        if news_limit is None:
            LOGGER.info("the limit doesn't set, the total number of news will be %s", news_on_page)
            news_limit = news_on_page
        elif news_limit > news_on_page:
            LOGGER.info("the limit is greater than news on page, the total number of news will be %s", news_on_page)
            news_limit = news_on_page
        return news_limit

    def _form_news_list_by_date(self, news_date: str, list_of_all_news: list) -> list:
        reformatted_date = str(dateutil_parser.parse(news_date, ignoretz=True).date())
        list_of_publication_dates = [
            str(dateutil_parser.parse(news.pubDate.string, ignoretz=True).date()) for news in list_of_all_news
        ]
        if reformatted_date not in list_of_publication_dates:
            raise ValueError("error: no news for the specified date")

        list_of_all_news_with_suitable_date = []
        for news_number, date in enumerate(list_of_publication_dates):
            if reformatted_date == date:
                list_of_all_news_with_suitable_date.append(list_of_all_news[news_number])

        news_limit = self._form_news_limit(list_of_news=list_of_all_news_with_suitable_date)
        return list_of_all_news_with_suitable_date[:news_limit]

    def _form_news_list(self, news_date: str) -> list:
        list_of_all_news = self._rss_page.find_all("item")
        if news_date is None:
            news_limit = self._form_news_limit(list_of_news=list_of_all_news)
            return list_of_all_news[:news_limit]
        return self._form_news_list_by_date(news_date=news_date, list_of_all_news=list_of_all_news)


def catch_exceptions(func):
    """Catch exceptions decorator.

    If an exception occurs, "_wrapped" sends an exception message to a logger and return None.
    Otherwise, it returns result of a decorated function.

    Args:
        func: decorated function

    Returns:
        result of the "_wrapped" function or None
    """

    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception as error:
            LOGGER.warning(error)
            return None
        return res

    return _wrapped


class ParserManager:
    """Main class of the rss-news reader."""

    def __init__(
            self,
            xml_page: None,
            news_limit: int = None,
            json_flag: bool = False,
            date: str = None,
            formats_and_paths: dict = None,
            colorized_mode: bool = False,
    ):
        """Initialize instances of the news former, the news news_handler, the news storage.

        "xml_page" == "None" means that news will be read from the news storage only.

        Args:
            xml_page: a BS4 xml-page or None is expected
            news_limit (int): limits the number of news to be processed. If None, all news on page will be processed
            json_flag (bool): if True, the news will be serialized to the json format
            date (str): date per which the news will be printed. If None, all processed news will be printed
            formats_and_paths (dict): file formats to convert news and paths to save this files
            colorized_mode (bool): if True, the console output will be printed in colorized mode
        """
        self._xml_page = xml_page
        self._json_flag = json_flag
        self._date = date
        self._formats_and_paths = formats_and_paths
        self._colorized_mode = colorized_mode

        if self._xml_page is not None:
            self.news_former = ParserNewsFormer(
                rss_page=self._xml_page,
                news_limit=news_limit,
                news_date=self._date,
            )

        self.news_handler = ParserNewsHandler()
        self.news_storage = NewsStorage(news_limit=news_limit)

    @catch_exceptions
    def start_processing(self):
        """Launch processing of rss-news.

        If the "self._xml_page" is not None, runs the "self._form_news()" method, forms news and saves them in a file.
        On the next step downloads this news from a file depending on a date.
        Expects returning of all news if date is None.

        Serialize and prints news if formats and paths is None.
        Otherwise, saves news to a files depending on a input formats.
        Serialize and prints news if "self._json_flag" is True.

        All exceptions catches by "catch_exceptions" decorator.

        Above steps expect the following signatures:

        "self._form_news" method expects the "form_news" method in the "self.news_former" class.
        The "form_news" method should return a list of news.
        "self.news_storage" should provide the "save_news_to_file" and "get_news_from_file" methods.

        "self._serialize_news" method expects the "serialize_news" and "register_data_format_to_process" methods
        in the "self.news_handler" class.
        "format_to_process" argument should receive an str.
        "news_to_serialize" argument should receive an iterable object.

        "self._print_news" method expects the "process_news" method in the "self.news_handler" class.
        "news_to_process" argument should receive an iterable object that can be processed by the class
        in the "news_handler" argument.
        "news_handler" argument expects a class with the "process_news" method.
        Also, "news_handler" "__init__" should contain "object_to_handle" and "data_format" arguments.

        "self._convert_news_to_files" method expects "register_data_format_to_process" and "process_news" methods
        in the "self.news_handler" class.
        "format_to_process" argument should receive an str.
        "news_to_process" argument should receive an iterable object that can be processed by the class
        in the "news_handler" argument.
        "news_handler" argument expects a class with the "process_news" method.
        """
        if self._xml_page is not None:
            self.news_storage.save_news_to_file(self._form_news())
        news_from_file = self.news_storage.get_news_from_file(news_date=self._date)

        if self._formats_and_paths is None:
            self._serialize_and_print_news(news_from_file)
        else:
            if self._json_flag:
                self._serialize_and_print_news(news_from_file)
            self._convert_news_to_files(news_to_convert=news_from_file)

    def _form_news(self) -> list:
        """Run "form_news" method from an "self.news_former" instance and return it's result.

        Returns:
            a list of formed news
        """
        return self.news_former.form_news()

    def _serialize_and_print_news(self, news: list) -> None:
        serialized_news = self._serialize_news(news_to_serialize=news)
        self._print_news(news_to_print=serialized_news)

    def _serialize_news(self, news_to_serialize: list) -> list:
        """Register serializing format and return serialized news.

        Args:
            news_to_serialize (list): a list of news to serialize

        Returns:
            a list of serialized news
        """
        self.news_handler.register_data_format_to_process(format_to_process="JSON" if self._json_flag else None)
        return self.news_handler.serialize_news(news_to_serialize=news_to_serialize)

    def _print_news(self, news_to_print: list) -> None:
        """Send news to process.

        The class in the "news_handler" argument must be able to handle "news_to_print"

        Args:
            news_to_print (list): a list of news to print

        Returns:
            None
        """
        return self.news_handler.process_news(
            news_to_process=(news_to_print, self._colorized_mode),
            news_handler=Printer,
        )

    def _convert_news_to_files(self, news_to_convert: list) -> None:
        """Register converting format and send news to process.

        The class in the "news_handler" argument must be able to handle "news_to_print"

        Args:
            news_to_convert (list): a list of news to convert in a files
        """
        for convert_format, path in self._formats_and_paths.items():
            if path is not None:
                self.news_handler.register_data_format_to_process(format_to_process=convert_format)
                self.news_handler.process_news(news_to_process=(path, news_to_convert), news_handler=FileConverter)
