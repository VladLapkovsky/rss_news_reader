"""This module provides news handlers."""

from abc import ABC, abstractmethod
from random import choice

import colorama

from rss_parser import colors
from rss_parser.file_converters.html_converter import HTMLConverter
from rss_parser.file_converters.pdf_converter import create_pdf
from rss_parser.logger import LOGGER
from rss_parser.news_separator import separate_news


def json_printer(news_to_process: tuple):
    """Print "JSON" news to stdout.

    Args:
        news_to_process (tuple): tuple like (news_to_print: list of news in the JSON format, colorized_mode: bool)
    """
    news_to_print = news_to_process[0]
    colorized_mode = news_to_process[1]
    if colorized_mode:
        colorama.init(autoreset=True)

    LOGGER.warning("printing news...")

    print(separate_news())
    for news in news_to_print:
        if colorized_mode:
            color = choice(colors.FORE)
            print(colorama.Fore.__getattribute__(color) + news)
        else:
            print(news)
        print(separate_news())


def human_readable_printer(news_to_process: tuple):
    """Print "LIST" news to stdout.

    Elements in list must be dictionaries. Function recognizes nested dictionaries.

    Args:
        news_to_process (tuple): tuple like (news_to_print: list of news in the DICT format, colorized_mode: bool)
    """
    news_to_print = news_to_process[0]
    colorized_mode = news_to_process[1]

    colorama.init()

    LOGGER.warning("printing news...")

    print(separate_news())

    def _dict_printer(dict_to_print: dict):
        for dict_key, dict_val in dict_to_print.items():
            if isinstance(dict_val, dict):
                print(dict_key.capitalize(), end=":\n")
                _dict_printer(dict_val)
            else:
                print(dict_key.capitalize(), dict_val, sep=": ")

    for news_container in news_to_print:
        print(colorama.Fore.__getattribute__(choice(colors.FORE) if colorized_mode else "RESET"))
        _dict_printer(news_container)
        print(colorama.Fore.RESET)
        print(separate_news())


class NewsHandler(ABC):
    """Abstract class. Provide process news logic.

    Inherited classes must redefine the "_register_formats" method and run
    "self.register_handler_format("DATA FORMAT", FUNCTION_TO_HANDLE)".

    Example: "DATA FORMAT": "JSON", FUNCTION_TO_HANDLE: json_printer
    """

    def __init__(self):
        """Provide "self._formats" to collect news_handler functions depending on the handling format.

        Run "self._register_formats()" method in an inherited class.
        """
        self._formats = {}
        self._register_formats()

    def process_news(self, object_to_handle, data_format: str):
        """Run a certain method in "self._formats" depending on the format of the "data_format".

        Args:
            object_to_handle (list): news to handle
            data_format (str): determine which news_handler function will process "object_to_handle"

        Returns:
            the result of processing the "object_to_handle" by the "handler_method" from "self._formats"
        """
        handler_method = self._formats.get(data_format)
        return handler_method(object_to_handle)

    def register_handler_format(self, data_format: str, data_handler):
        """Save "data_format" and "data_handler" in "self._formats".

        Args:
            data_format (str): defines the key under which the news_handler function is saved
            data_handler: determine the news_handler function
        """
        self._formats[data_format] = data_handler

    @abstractmethod
    def _register_formats(self):
        """Provide the "_register_formats" method as a required interface."""


class Printer(NewsHandler):
    """Inheritor of the "NewsHandler" abstract class.

    Redefine the "_register_formats" method and register "JSON" and "LIST" printers.
    """

    def _register_formats(self):
        self.register_handler_format("LIST", human_readable_printer)
        self.register_handler_format("JSON", json_printer)


class FileConverter(NewsHandler):
    """Inheritor of the "NewsHandler" abstract class.

    Redefine the "_register_formats" method and register "TO_HTML" and "TO_PDF" converters.
    """

    def _register_formats(self):
        self.register_handler_format("TO_HTML", HTMLConverter)
        self.register_handler_format("TO_PDF", create_pdf)
