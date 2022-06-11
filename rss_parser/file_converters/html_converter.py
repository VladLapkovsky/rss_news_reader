"""This module provides news converting to the .html file with jinja2."""

import os
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape

from rss_parser.logger import LOGGER


def regex_remove_square_brackets(description: str) -> str:
    """Jinja2 filter removes square brackets in the news description.

    Example:
    description: "[image 2: image description] blah-blah" -> "blah-blah"

    Args:
        description (str): the string to which the filter is to be applied

    Returns:
        the string without square brackets
    """
    pattern = r"\[.*\]"
    return re.sub(pattern, "", description)


def regex_image_description(description: str, image_number: int) -> str:
    """Jinja2 filter removes the news description and leaves the image caption.

    Example:
    image_number == 2
    description: "[image 2: image 2 description][2][image 3: image 3 description][3] blah-blah" -> "image 2 description"

    Args:
        description (str): the string to which the filter is to be applied
        image_number (int): the image number

    Returns:
        the string only with image caption or "no description"
    """
    pattern = fr"(?<=image\s{image_number}:\s)(.*?)(?=\])"
    try:
        return re.search(pattern, description).group()
    except AttributeError:
        return "no description"


def regex_remove_image_text_in_brackets(url: str) -> str:
    """Jinja2 filter removes round brackets in the url.

    Example:
    [1]: "url (image)" -> "url"

    Args:
        url (str): the string to which the filter is to be applied

    Returns:
        the string without round brackets
    """
    pattern = r"\s\(image\)"
    return re.sub(pattern, "", url)


class HTMLConverter:
    """Class to convert news to the .html file by the template."""

    def __init__(self, news_to_convert: tuple):
        """Provide initialization and launch conversion to the .html file.

        Create html template from "templates" folder.
        Register html filters and run the .html file creation.

        Args:
            news_to_convert (tuple): expect tuple like (path, news to convert)
        """
        self.path = news_to_convert[0]
        self.news = news_to_convert[1]

        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_templates = os.path.sep.join((current_dir, "templates/"))

        self.env = Environment(loader=FileSystemLoader(path_to_templates), autoescape=select_autoescape())
        self._register_filters()
        self.template = self.env.get_template("html_template.html")

        self.create_html_file()

    def create_html_file(self):
        """Render .html file and save it to a file by path."""
        LOGGER.warning("converting news to HTML...")

        html_file = self.template.render(news_list=self.news)

        file_name = os.path.sep.join((self.path, "news.html"))
        with open(file_name, "w") as output_file:
            output_file.writelines(html_file)

    def _register_filters(self):
        self.env.filters["regex_remove_square_brackets"] = regex_remove_square_brackets
        self.env.filters["regex_image_description"] = regex_image_description
        self.env.filters["regex_remove_image_text_in_brackets"] = regex_remove_image_text_in_brackets
