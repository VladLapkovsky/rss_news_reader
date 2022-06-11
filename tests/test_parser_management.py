"""This module provides tests for "news_object.py"."""

import json
import os
import sys

import pytest

sys.path.append(os.getcwd())

from rss_parser import parser_management


@pytest.fixture
def news_handler():
    """Prepare "__init__".

    Returns:
        prepared instance
    """
    return parser_management.ParserNewsHandler()


@pytest.mark.parametrize(
    "data_to_check",
    [
        pytest.param(
            [{"1": "2"}],
        ),
        pytest.param(
            [{1: 2}],
        ),
    ],
)
def test_serializing_json_ok(news_handler, data_to_check):
    """Test the converting to JSON with "serialize_news" method using different data, which have passed the test.

    Args:
        news_handler: prepared class instance
        data_to_check: example data to check
    """
    prepared_news = data_to_check[:]
    prepared_news[0] = json.dumps(prepared_news[0], indent=4)
    news_handler.register_data_format_to_process("JSON")
    assert prepared_news == news_handler.serialize_news(data_to_check)


@pytest.mark.parametrize(
    "data_to_check",
    [
        pytest.param(
            [{"1": "2"}],
        ),
        pytest.param(
            [{1: 2}],
        ),
    ],
)
def test_serializing_json_bad(news_handler, data_to_check):
    """Test the converting to JSON with "serialize_news" method using different data, which have not passed the test.

    Args:
        news_handler: prepared class instance
        data_to_check: example data to check
    """
    prepared_news = data_to_check[:]
    prepared_news[0] = json.dumps(prepared_news[0])
    assert prepared_news != news_handler.serialize_news(data_to_check)


@pytest.mark.parametrize(
    "data_to_check",
    [
        pytest.param(
            [{"1": "2"}],
        ),
        pytest.param(
            [{1: 2}],
        ),
    ],
)
def test_serializing_list_ok(news_handler, data_to_check):
    """Test the "serialize_news" without converting to JSON method using different data, which have passed the test.

    Args:
        news_handler: prepared class instance
        data_to_check: example data to check
    """
    prepared_news = data_to_check[:]
    assert prepared_news == news_handler.serialize_news(data_to_check)
