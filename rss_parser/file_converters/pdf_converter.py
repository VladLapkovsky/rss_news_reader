"""This module provides news converting to the .pdf file with fpdf."""

import mimetypes
import os
import re
from functools import wraps

import requests
from fpdf import FPDF

from rss_parser.logger import LOGGER

DEFAULT_FONT = "DejaVu"


def set_default_font_after_operation(func):
    """Pdf creation decorator.

    Sets the font after executing the function.

    Use it if a function changes font.

    Args:
        func: decorated function

    Returns:
        result of the "_wrapped" function
    """

    @wraps(func)
    def _wrapped(*args, **kwargs):
        res = func(*args, **kwargs)
        pdf = kwargs["pdf"]
        pdf.set_font(family=DEFAULT_FONT, style="", size=12)
        return res

    return _wrapped


def add_link(pdf, news_dict: dict):
    """Add a news article link to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
    """
    link = news_dict["link"]
    pdf.multi_cell(w=0, h=5, txt=f"Source: {link}")
    pdf.ln(h=5)


def add_description(pdf, news_dict: dict):
    """Add a news article description to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
    """
    description = news_dict["description"]
    pattern = r"\[.*\]"
    description = re.sub(pattern, "", description).strip()
    # "[image image_number: image_caption] description" -> "description"
    pdf.multi_cell(w=0, h=5, txt=description)
    pdf.ln(h=5)


@set_default_font_after_operation
def add_caption(pdf, description: str, image_counter: int):
    """Add an image caption to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        description (str): a news article description
        image_counter (int): an image number to get certain image caption
    """
    pattern = fr"(?<=image\s{image_counter}:\s)(.*?)(?=\])"
    try:
        image_caption = re.search(pattern=pattern, string=description).group()
        # "[image image_counter: image_caption] description" -> "image_caption"
    except AttributeError:
        image_caption = "no description"
    pdf.set_font(family=DEFAULT_FONT, style="", size=10)
    pdf.multi_cell(w=0, h=5, txt=image_caption)
    pdf.ln(h=5)


def add_url_image_instead_of_image(pdf, image_url: str):
    """Add an image url to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        image_url (str): an image url from a news article
    """
    pdf.multi_cell(w=0, h=5, txt=image_url)
    pdf.ln(h=5)


COUNTER = 0


def add_image(pdf, session: requests.Session, image_url: str):
    """Add news article images to the pdf instance.

    Gets an image by its url.
    Detects an image extension.
    Writes response as binary data in an image file with unique name in the current file folder.
    Adds this image to the pdf instance.
    Deletes this image.

    Adds an image url instead of an image, if the pdf file is created when the Internet is not available.

    The global "COUNTER" is required for the correct work of image inserting .

    Args:
        pdf: the instance of the FPDF class
        session: requests session
        image_url (str): an image url from a news article
    """
    global COUNTER

    pattern = r"\s\(image\)"
    news_image_link = re.sub(pattern=pattern, repl="", string=image_url)  # remove " (image)" from image url

    try:
        image_response = session.get(url=news_image_link)
    except requests.exceptions.ConnectionError:
        add_url_image_instead_of_image(pdf=pdf, image_url=news_image_link)
    else:
        content_type = image_response.headers["content-type"]
        extension = mimetypes.guess_extension(content_type)  # get image extension

        file_path = os.path.abspath(os.path.dirname(__file__))
        file_name = str(COUNTER) + extension
        full_file_path = os.path.sep.join((file_path, file_name))

        with open(full_file_path, "wb") as out_file:
            out_file.write(image_response.content)
        try:
            pdf.image(name=full_file_path, w=1920 / 40, type="", link=news_image_link)
            # "w" sets the aspect ratio of the image
        except RuntimeError:
            add_url_image_instead_of_image(pdf=pdf, image_url=news_image_link)
        os.remove(full_file_path)
    COUNTER += 1


def add_images_and_captions(pdf, news_dict: dict):
    """Add news article images and its captions to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
    """
    links = news_dict["links"]
    if len(links) > 1:
        session = requests.Session()
        image_counter = 2
        for url in links.values():
            if "(link)" in url:
                continue
            add_image(pdf=pdf, session=session, image_url=url)
            add_caption(pdf=pdf, description=news_dict["description"], image_counter=image_counter)
            image_counter += 1


@set_default_font_after_operation
def add_date(pdf, news_dict: dict):
    """Add a news article date to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
    """
    date = news_dict["date"]
    pdf.multi_cell(w=0, h=5, txt=date)
    pdf.ln(h=5)


@set_default_font_after_operation
def add_title(pdf, news_dict: dict, news_number: int):
    """Add a news article title to the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
        news_number (int): a news article number
    """
    news_article_title = news_dict["title"]
    txt_title = ": ".join((str(news_number + 1), news_article_title))

    pdf.set_font(family=DEFAULT_FONT, style="", size=16)
    pdf.multi_cell(w=0, h=5, txt=txt_title)
    pdf.ln(h=5)


def add_news_article(pdf, news_dict: dict, news_number: int):
    """Create a single news article in the pdf instance.

    Args:
        pdf: the instance of the FPDF class
        news_dict (dict): a single news article
        news_number (int): a news article number
    """
    pdf.set_line_width(width=0)  # create top border of the news article
    pdf.line(x1=0, y1=pdf.get_y(), x2=210, y2=pdf.get_y())
    pdf.ln(h=5)

    add_title(pdf=pdf, news_dict=news_dict, news_number=news_number)
    add_date(pdf=pdf, news_dict=news_dict)
    add_images_and_captions(pdf=pdf, news_dict=news_dict)
    add_description(pdf=pdf, news_dict=news_dict)
    add_link(pdf=pdf, news_dict=news_dict)

    pdf.line(x1=0, y1=pdf.get_y(), x2=210, y2=pdf.get_y())  # create bottom border of the news article


class CustomPDF(FPDF):
    """Inheritor of the "FPDF" class.

    Creates the header and the footer of the .pdf file.
    """

    def __init__(self):
        """Add default font to the pdf instance to handle unicode characters."""
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_font = os.path.sep.join((current_dir, "fonts", "DejaVuSansCondensed.ttf"))
        self.add_font(family=DEFAULT_FONT, style="", fname=path_to_font, uni=True)

    def header(self):
        """Add pdf header."""
        self.set_font(family=DEFAULT_FONT, style="", size=12)
        self.cell(w=0, h=-10, txt="Vladsilav Lapkovsky", ln=1, link="https://github.com/VladLapkovsky")
        self.set_line_width(width=1.0)
        self.line(x1=0, y1=10, x2=210, y2=10)
        self.ln(h=15)

    def footer(self):
        """Add pdf footer."""
        self.set_y(y=-10)
        self.set_font(family=DEFAULT_FONT, style="", size=8)

        page = str(self.page_no()).join(("Page ", "/{nb}"))
        self.cell(w=0, h=10, txt=page, border=0, ln=0, align="C")


def create_pdf(news_to_convert: tuple):
    """Run logic of the .pdf creation.

    Main function of the .pdf creation.

    Creates the FPDF instance.
    Adds the rss-news title and the news articles.
    Saves the news to the .pdf file.

    Args:
        news_to_convert (tuple): expect tuple like "(path, news to convert)"
    """
    LOGGER.warning("converting news to PDF...")

    path = news_to_convert[0]
    news = news_to_convert[1]

    pdf = CustomPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font(family=DEFAULT_FONT, style="", size=18)
    rss_news_title = news[0]["feed"]
    pdf.multi_cell(w=0, h=10, txt=rss_news_title)  # add rss-news title

    pdf.set_font(family=DEFAULT_FONT, style="", size=12)
    for news_number, news_dict in enumerate(news):
        add_news_article(pdf=pdf, news_dict=news_dict, news_number=news_number)

    pdf.output(os.path.sep.join((path, "news.pdf")))
