"""This module provides the "WebParser" class for parsing and several functions to it."""

import re
from functools import wraps
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from rss_parser.logger import LOGGER
from rss_parser.web_parser.data_checkers import html_data_checker


def suppress_exceptions(func):
    """Suppress exceptions decorator.

    If exception occurs, "_wrapped" returns None.

    Args:
        func: decorated function

    Returns:
        the "_wrapped" function
    """

    @wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception:
            return None
        return res

    return _wrapped


@suppress_exceptions
def description_header_two(soup) -> str:
    """Return the first "header 2" from web page.

    Args:
        soup: html web page, downloaded by BeautifulSoup

    Returns:
        soup.h2.string
    """
    return soup.h2.string


@suppress_exceptions
def description_title(soup) -> str:
    """Return the title tag content from web page.

    Args:
        soup: html web page, downloaded by BeautifulSoup

    Returns:
        soup.title.string
    """
    return soup.title.string


@suppress_exceptions
def description_property_og(soup) -> str:
    """Return the first "meta" tag with specific property.

    Args:
        soup: html web page, downloaded by BeautifulSoup

    Returns:
        soup.find("meta", property="og:description")["content"]
    """
    description = soup.find("meta", property="og:description")["content"]
    return re.sub("<.*?>", "", description)


@suppress_exceptions
def description_tag_p_class_lead(soup) -> str:
    """Return the first "p" tag with the "lead" class.

    Args:
        soup: html web page, downloaded by BeautifulSoup

    Returns:
        soup.find("p", "lead").text
    """
    return soup.find("p", "lead").text


@suppress_exceptions
def description_meta_tag(soup) -> str:
    """Return the first "meta" tag with description content.

    Args:
        soup: html web page, downloaded by BeautifulSoup

    Returns:
        soup.find("meta", {"name": "description"}).attrs["content"]
    """
    return soup.find("meta", {"name": "description"}).attrs["content"]


class WebParser:
    """Class for parsing rss-news.

    It uses "requests" and "BS4" libraries.
    """

    def __init__(self, url: str, parser_mode: str):
        """Download page and parse it.

        Args:
            url (str): url of the web page
            parser_mode (str): determine the way the parser class downloads data from web page

        """
        self.url = url
        self._page = requests.get(self.url)
        self.soup = BeautifulSoup(self._page.content, features=parser_mode)

    def form_img_data(self) -> list:
        """Form image container.

        "self._collect_img_tag_images" finds all "img" tags on page, sends them to "html_data_checker" and collects
        "(image, image_caption)" in "images_container". If the check fails, then the tag elements are ignored.

        "self._collect_a_href_tag_images" finds all "a href" links on page. If links are in the "href" tags and
        end with ".jpg", ".png", they are saved in "images_container" with empty caption.

        Returns:
            list (may be empty) of "(image, image_caption)"
        """
        images_container = []
        images_container += self._collect_img_tag_images()
        images_container += self._collect_a_href_tag_images()
        return images_container

    def form_description(self) -> str:
        """Return news description.

        Define list of a few description formers. The order in "description_formers" matters.
        If none of description formers doesn't find description, the html page title will be returned.

        Returns:
            description from rss or html page
        """
        description_formers = [
            description_meta_tag,
            description_tag_p_class_lead,
            description_property_og,
            description_title,
            description_header_two,
        ]
        for description_former in description_formers:
            description = description_former(self.soup)
            if description:  # expect None or normal description in result of "description_former"
                return description
        return self.soup.title.string

    def _collect_img_tag_images(self) -> list:
        images_container = []
        try:
            collected_tags = self.soup.findAll("img")
        except AttributeError:
            LOGGER.info("the news web page doesn't have 'img' tags...")
        else:
            for collected_tag in collected_tags:
                image_url, caption = get_img_data(tag=collected_tag, instance_flag=self, page_url=self.url)
                if image_url:  # check only image_url because empty caption is allowed
                    images_container.append((image_url, caption))
        return images_container

    def _collect_a_href_tag_images(self) -> list:
        images_container = []
        for link in self.soup.findAll("a"):
            a_href = link.get("href")
            if a_href and a_href.endswith((".jpg", ".png")):
                images_container.append((a_href, ""))
        return images_container


def get_img_data(tag, instance_flag, page_url: str):
    """Check "img" tag for data correctness.

    Recognise image urls like "/image/image.jps". In this case add domain to the image url and check it for correct
    extension. Only nested urls that end with "jpg" and "png" are allowed.

    Args:
        tag: "img" tag
        instance_flag: the flag that shows to which instance the tag belongs
        page_url: web page url, used to check nested urls

    Returns:
        image url and image caption if they are not empty else None, None
    """
    if html_data_checker(tag=tag, instance_flag=instance_flag):
        image_url = tag.get("src")
        caption = tag.get("alt")
        nested_url = get_nested_url(tag=tag, page_url=page_url)
        if nested_url and nested_url.endswith(("jpg", "png")):
            image_url = nested_url
        try:
            requests.get(image_url)
        except (
                requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError,
        ):
            return None, None
        return image_url, caption
    return None, None


def get_nested_url(tag, page_url: str):
    """Check image url for nesting.

    Works for urls like "/image/image.jps". In this case add domain to the image url and check its status code.

    Args:
        tag: "img" tag
        page_url: web page url, used to check nested urls

    Returns:
        nested url if it doesn't return 404 status code else None
    """
    domain = urlparse(page_url)
    image_url = tag.get("src")
    nested_url = f"{domain.scheme}://{domain.netloc}/" + image_url
    resp = requests.get(nested_url)
    return None if resp.status_code == 404 else nested_url
