"""This module provides a class to form and save a single news object."""

import re

from bs4 import BeautifulSoup
from dateutil import parser as dateutil_parser

from rss_parser.logger import LOGGER


class NewsObject:
    """A class that forms and saves a single news object."""

    def __init__(self, title: str, certain_rss_news, parser, parser_mode: str = "lxml"):
        """Provide "NewsObject" initialization.

        "self._title" is used to form general news "feed".
        Example: Yahoo News - Latest News & Headlines.

        "self._certain_rss_news" is used to get a data from a certain news article,
        like news "title", "description", "date", "link".

        "parser" should contain "url" and "parser_mode" arguments in "__init__".
        "parser" should provide "form_images", "form_description" methods.
        "form_images" must return an iterable object with pairs "(image_url, image_caption)".

        Args:
            title: rss-page title
            certain_rss_news: certain news article (BS4 "item" tag is expected)
            parser: a class for downloading data from web page (a class that uses BS4 is expected)
            parser_mode (str): determine the way the parser class downloads data from an html page
        """
        self.news_container = {}

        self._title = title

        self._certain_rss_news = certain_rss_news

        self._img_data_container = self._collect_img_data(parser=parser, parser_mode=parser_mode)

    def form_news(self):
        """Run forming news logic by filling the "self.news_container".

        "self._form_header" collects "feed", "title", "date", "link".
        "date" attr is provided as a property. It uses "dateutil" module to convert publication date
        into a common format.

        "self._form_description" forms description from "self._img_data_container" (if "link" tag is exist).
        If description in "self._img_data_container" is empty, the description is replaced by "no description".
        Gets description from rss-tag "description" if its exist.
        Otherwise calls the the "form_description" method from "self._parser".

        "self._form_links" forms links from "self._img_data_container".

        "self.news_container" provides the following structure:

        Feed: "feed"

        Title: "title"

        Date: "date"

        Link: "link"

        Description: "description"

        Links:

        [1]: "link" (link to the news html page)

        [2]: "link" (link to image on page if image exists)

        ...
        """
        self._form_header()
        self._form_description()
        self._form_links()

    @property
    def date(self) -> str:
        """Reform original date from rss-article to a common format.

        The common format is "%Y-%m-%d %H:%M:%S.

        Returns:
            a publish date in str format
        """
        date_time_str = self._certain_rss_news.pubDate.string
        date_time_obj = dateutil_parser.parse(date_time_str, ignoretz=True)
        return str(date_time_obj.replace(tzinfo=None))

    def _collect_img_data(self, parser, parser_mode: str) -> list:
        try:
            self._html_url = self._certain_rss_news.link.string
        except AttributeError:
            log_err = "rss-page doesn't provide supported interface, tag <link> is missing. "
            log_msg = "News will be printed without news link"
            LOGGER.info("%s", log_err + log_msg)
            return None
        self._parser = parser(url=self._html_url, parser_mode=parser_mode)
        return self._parser.form_img_data()

    def _form_header(self):
        LOGGER.info("forming news header...")
        self.news_container.update({"feed": self._title + "\n"})
        self.news_container.update({"title": self._certain_rss_news.title.string})
        self.news_container.update({"date": self.date})

        if self._img_data_container is not None:
            news_link = self._certain_rss_news.link.string
        else:
            news_link = "Rss news doesn't provide link"
        self.news_container.update({"link": news_link + "\n"})

    def _form_description(self):
        LOGGER.info("forming news description...")
        description = ""
        counter = 2
        if self._img_data_container is not None:
            for _image_url, caption in self._img_data_container:
                caption = caption if caption else "no description"
                description += f"[image {counter}: {caption}][{counter}]"
                counter += 1
        try:
            rss_description = self._certain_rss_news.description.string
        except AttributeError:  # if tag <description> is not exist
            description += self._parser.form_description() + "\n"
        else:
            if rss_description is not None:
                description += re.sub("<.*?>", "", rss_description) + "\n"  # remove tags (<>) from description
            else:
                description += self._parser.form_description() + "\n"
        soup = BeautifulSoup(description, "lxml")  # to hide symbols like &#39 in str description
        self.news_container.update({"description": soup.get_text()})

    def _form_links(self):
        LOGGER.info("forming news links...")
        links = {}
        if self._img_data_container is not None:
            links.update({"[1]": self._html_url + " (link)"})
            counter = 2
            for image_url, _caption in self._img_data_container:
                links.update({f"[{counter}]": image_url + " (image)"})
                counter += 1
        else:
            links.update({"[1]": "Rss news doesn't provide link"})
        self.news_container.update({"links": links})
