"""This module provides tests for "news_object.py"."""

import os
import sys
from unittest import mock

import pytest

sys.path.append(os.getcwd())

from rss_parser.news_object import NewsObject
from rss_parser.web_parser.web_parser import WebParser


@pytest.fixture
def mock_web_parser():
    """Prepare mocked object of WebParser.

    Returns:
        mocked WebParser class
    """
    return mock.Mock(spec=WebParser)


@pytest.fixture
def news_object(mock_web_parser):
    """Prepare mocked instance of NewsObject "__init__".

    Args:
        mock_web_parser: mocked object of WebParser

    Returns:
        mocked NewsObject instance
    """
    return NewsObject(
        title=mock.MagicMock(),
        certain_rss_news=mock.MagicMock(),
        parser=mock_web_parser,
        parser_mode=mock.MagicMock(),
    )


def test_news_object_news_container(news_object):
    """Check "news_container" type.

    Args:
        news_object: mocked NewsObject instance
    """
    assert isinstance(news_object.news_container, dict)


@mock.patch.object(NewsObject, "date")
@mock.patch.object(NewsObject, "_form_description")
def test_news_object_form_news_dont_change_type_of_news_container(mock_date, mock_descr, news_object):
    """Test that NewsObject doesn't change original type of "news_container" after running "form_news".

    Args:
        mock_date: mocked "_date" property of NewsObject
        mock_descr: mocked "_form_description" method of NewsObject
        news_object: mocked NewsObject instance
    """
    news_object._img_data_container = mock.MagicMock()
    news_object.form_news()
    assert isinstance(news_object.news_container, dict)
