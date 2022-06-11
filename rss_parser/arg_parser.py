"""This module provides "argparse" initialization and checkers to its parameters.

"ArgsChecker" calls the next classes:
    PageChecker: checks page for availability and rss-news. Call URLChecker to checks the url for correctness
    LimitChecker: checks the limit value for correctness
    LimitChecker: checks the date value for correctness
"""

import argparse
import os
from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser

from rss_parser.logger import LOGGER


class Checker(ABC):
    """Abstract class for checkers.

    Inherited classes must redefine the "check" method.
    """

    @abstractmethod
    def check(self):
        """Provide the "check" method as a required interface."""


class PathsForConversionsChecker(Checker):
    """Check paths for existence."""

    def __init__(self, formats_and_paths: dict):
        """Expect formats_and_paths in the "dict" format, where key is convert format and value is file path.

        Args:
            formats_and_paths (dict): paths to check for existence
        """
        self.formats_and_paths = formats_and_paths

    def check(self) -> bool:
        """Check paths for existence.

        Skip path if path is None.

        Raises:
            ValueError: if input path doesn't exist

        Returns:
            True check is passed
        """
        for convert_format, path in self.formats_and_paths.items():
            if path is None:
                continue
            LOGGER.info("checking '%s' path...", convert_format)
            if not os.path.exists(path):
                raise ValueError(f"error: the input path for '{convert_format}' format doesn't exist")
        return True


class DateChecker(Checker):
    """Check date value for correctness."""

    def __init__(self, date_to_check: str):
        """Expect date in the "str" format, which match to '%Y%m%d' pattern.

        Args:
            date_to_check (str): date to check for correctness
        """
        self.date_to_check = date_to_check

    def check(self) -> bool:
        """Run methods to check date.

        "self._check_date_value" checks if date match to '%Y%m%d' pattern. Raise "ValueError" if it's not.
        "self._check_date_format" checks if date match to '20210102' format (day and month from 01 to 09 with 0).
        Raise "ValueError" if it's not.

        Returns:
            True if all checks are passed
        """
        if self.date_to_check is None:
            return True
        LOGGER.info("checking date...")
        self._check_date_value()
        self._check_date_format()
        return True

    def _check_date_value(self) -> bool:
        date_pattern = "%Y%m%d"
        try:
            datetime.strptime(self.date_to_check, date_pattern)
        except ValueError as error:
            raise ValueError("error: the date doesn't confirm to '%Y%m%d' pattern") from error
        return True

    def _check_date_format(self) -> bool:
        try:
            dateutil_parser.parse(self.date_to_check).date()
        except ValueError as error:
            raise ValueError(
                "error: please use date in format like '20210102' (day and month from 01 to 09 with 0)",
            ) from error
        return True


class LimitChecker(Checker):
    """Check limit value for correctness."""

    def __init__(self, limit: str):
        """Expect limit in the "str" format, which could be formed to int.

        Args:
            limit (str): value to check for correctness
        """
        self.limit = limit

    def check(self) -> bool:
        """Run methods to check limit.

        "self._check_limit_type" checks if limit is an integer. Raise "ValueError" if it's not.
        "self._check_limit_value" checks if limit greater than zero. Raise "ValueError" if it's not.

        Returns:
            True if all checks are passed
        """
        if self.limit is None:
            return True
        LOGGER.info("checking limit...")
        self._check_limit_type()
        self._check_limit_value()
        return True

    def _check_limit_type(self) -> bool:
        try:
            int(self.limit)
        except ValueError as error:
            raise ValueError("error: the limit must be an integer") from error
        return True

    def _check_limit_value(self) -> bool:
        if int(self.limit) <= 0:
            raise ValueError("error: the limit must be greater than zero")
        return True


class URLChecker(Checker):
    """Check url for correctness."""

    def __init__(self, url: str):
        """Expect url in "http(s)://" format.

        Args:
            url (str): news url to check
        """
        self.url = url

    def check(self) -> bool:
        """Run methods to check url for correctness.

        "self._check_url_has_http" checks the url for http. Raise "ValueError" if there is no "http" in the url.
        "self._check_url_is_correct" uses the "urllib.parse" module to check url.
        Raise "ValueError" if "urllib" check fails.

        Returns:
            True if all checks are passed
        """
        if self.url is None:
            return True
        LOGGER.info("checking url for correctness...")
        self._check_url_has_http()
        self._check_url_is_correct()
        return True

    def _check_url_has_http(self) -> bool:
        if "http" in self.url:
            return True
        raise ValueError(
            f"error: invalid source: check the website address for correctness. Perhaps you meant http://{self.url}?",
        )

    def _check_url_is_correct(self) -> bool:
        parsed_url = urlparse(self.url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("error: invalid source: check the website address for correctness")
        return True


class PageChecker(URLChecker):
    """Check page for availability and rss-news."""

    def __init__(self, url: str, timeout: int = 3):
        """Expect url in "http(s)://" format.

        Args:
            url (str): page to check for availability
            timeout (int): the time (in sec) the page is given to send a response
        """
        super().__init__(url=url)
        self.url = url
        self._timeout = timeout

    def check(self) -> bool:
        """Run super check method and methods to check url for availability and rss-news.

        "self._check_connection" checks page for availability.
        Raise "TimeoutError" if response time exceeds the timeout.

        "self._check_page_is_rss" checks page for rss-tag. Raise "ValueError" if the website doesn't provide RSS-news.

        Returns:
            True if all checks are passed
        """
        if self.url is None:
            return True
        super().check()
        resp = self._check_connection()
        soup = BeautifulSoup(resp.content, "xml")
        self._check_page_is_rss(soup)
        return True

    def _check_connection(self) -> requests.models.Response:
        LOGGER.info("checking connection to the site...")
        try:
            resp = requests.get(self.url, timeout=self._timeout)
        except requests.exceptions.ConnectionError:
            error = "error: can't get access to the website: "
            error_msg = "check the website availability, your internet connection and try again"
            raise TimeoutError(
                error + error_msg,
            ) from requests.exceptions.ConnectionError
        if resp.status_code == 403:
            raise ValueError("error: 403 Forbidden, can't connect to the server at this time")
        if resp.status_code == 404:
            raise ValueError("error: 404 Not Found, page not found")
        return resp

    def _check_page_is_rss(self, soup):
        LOGGER.info("checking for rss-news...")
        rss_tag = soup.rss
        if rss_tag is not None:
            return True
        raise ValueError("error: invalid source: the website should provide RSS-news")


class ArgsChecker:
    """Check argparse arguments.

    If any of the checks fail, the exception with specific message will be raised and the program will stop.
    """

    def __init__(self, url: str, limit: str, date: str, formats_and_paths: dict):
        """Initialize list with checkers instances.

        Args:
            url (str): news url to check
            limit (str): news limit to check
            date (str): news date to check
            formats_and_paths (dict): dict with file formats and paths to conversion

        Raises:
            ValueError: if both of url and date are None
        """
        if url is None and date is None:
            raise ValueError("error: the following arguments are required: source or --date, type '--help' for help")
        LOGGER.info("initiate input parameters checking system...")
        self._instances_to_check_args = [
            PageChecker(url=url),
            LimitChecker(limit=limit),
            DateChecker(date_to_check=date),
            PathsForConversionsChecker(formats_and_paths=formats_and_paths),
        ]

    def check(self) -> bool:
        """Run checking process.

        It uses common interface of checkers' classes.
        All checkers' classes in "self._instances_to_check_args" must contain the "check" method without parameters
        and raise exceptions if checks fail.

        Example:
        class OneMoreCheck:
        def check(self): ...

        If any of the checks fail, the exception with specific message will be raised and the program will stop.
        Else return True.

        Returns:
            True if all checks are passed
        """
        LOGGER.info("checking input parameters...")
        for class_name in self._instances_to_check_args:
            class_name.check()
        LOGGER.info("checking input parameters is complete, everything is OK...")
        return True


def init_argparse() -> argparse.Namespace:
    """3-*Initialize argparse arguments.

    Usage: rss_reader.py [-h] [--version] [--json] [--verbose] [--limit LIMIT]
    [--date [DATE]] [--to-html TO_HTML] [--to-pdf TO_PDF] [--colorize] [source]

    Vars:
        source: url of the site to read rss-news

        -h, --help: prints help message and exits

        --version: prints version info and exits

        --json: prints result as JSON in stdout. Find the JSON structure in the README file

        --verbose: outputs verbose status messages

        --limit LIMIT: limits news topics if this parameter is provided

        --date [DATE]: outputs news for the specified date

        --to-html TO_HTML: saves news to .html file by the specified path

        --to-pdf TO_PDF: saves news to .pdf file by the specified path

        --colorize: prints the console result of the utility in colorized mode

    Returns:
        Initialized arguments
    """
    parser = argparse.ArgumentParser(description="Pure Python command-line RSS reader.")
    parser.add_argument("url", metavar="source", nargs="?", help="RSS URL")
    parser.add_argument("--version", action="version", version="RSS-reader 5.0.0", help="Prints version info")
    parser.add_argument("--json", action="store_true", help="Prints result as JSON in stdout")
    parser.add_argument("--verbose", action="store_true", help="Outputs verbose status messages")
    parser.add_argument("--limit", help="Limit news topics if this parameter provided")
    parser.add_argument("--date", nargs="?", help="Outputs news for the specified date")
    parser.add_argument("--to-html", help="Saves news to .html file by the specified path")
    parser.add_argument("--to-pdf", help="Saves news to .pdf file by the specified path")
    parser.add_argument(
        "--colorize", action="store_true", help="Prints the console result of the utility in colorized mode",
    )
    return parser.parse_args()
