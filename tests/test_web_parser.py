"""This module provides tests for "web_parser.py"."""

import os
import sys

import pytest

sys.path.append(os.getcwd())

from rss_parser.web_parser.web_parser import WebParser


@pytest.fixture
def web_page(request):
    """Prepare "__init__".

    Args:
        request: fixture parameter, "request.param" accept url

    Returns:
        prepared instance
    """
    return WebParser(url=request.param, parser_mode="lxml")


@pytest.mark.parametrize(
    "web_page",
    [
        "https://news.yahoo.com/rss/",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    indirect=True,
)
def test_form_img_data_is_list(web_page):
    """Check type of result of "_collect_img_tag_images" method.

    Args:
        web_page: prepared WebParser instance
    """
    parser = web_page._collect_img_tag_images()
    assert isinstance(parser, list)


@pytest.mark.parametrize(
    "web_page",
    [
        "https://www.python.org/",
        "http://feeds.bbci.co.uk/news/world",
    ],
    indirect=True,
)
def test_form_img_data_without_img_tag(web_page):
    """Test that the "form_images" method returns empty list from non rss-news.

    Args:
        web_page: prepared WebParser instance
    """
    parser = web_page.form_img_data()
    assert list() == parser


@pytest.mark.parametrize(
    "web_page",
    [
        "https://www.python.org/",
        "http://feeds.bbci.co.uk/news/world",
    ],
    indirect=True,
)
def test_form_description_return_str(web_page):
    """Test that the "form_description" method returns expected type of data.

    Args:
        web_page: prepared WebParser instance
    """
    parser = web_page.form_description()
    assert isinstance(parser, str)


@pytest.mark.parametrize(
    "web_page",
    [
        "https://www.python.org/",
    ],
    indirect=True,
)
def test_form_description_correct_desc_python_org(web_page):
    """Test that the "form_description" method returns expected result.

    Args:
        web_page: prepared WebParser instance
    """
    parser = web_page.form_description()
    expected_value = "The official home of the Python Programming Language"
    assert parser == expected_value
