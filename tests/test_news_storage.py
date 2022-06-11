"""This module provides tests for "news_storage.py"."""

import os
import sys

import pytest

sys.path.append(os.getcwd())

from rss_parser.news_storage import NewsStorage


@pytest.fixture
def news_storage(request):
    """Prepare "__init__".

    Args:
        request: fixture parameter, "request.param" accept "news_limit" and "file_name"

    Returns:
        prepared instance
    """
    return NewsStorage(news_limit=request.param[0], file_name=request.param[1])


@pytest.mark.parametrize(
    "news_storage",
    [
        (None, "hello"),
        (123, ""),
    ],
    indirect=True,
)
def test_path_to_save_file(news_storage):
    """Test that the NewsStorage class gets correct path.

    Args:
        news_storage: the NewsStorage instance
    """
    current_path = os.getcwd() + os.path.sep
    assert current_path + news_storage.file_name == news_storage.path


@pytest.mark.parametrize(
    "news_storage",
    [
        (None, "hello.txt"),
    ],
    indirect=True,
)
@pytest.mark.parametrize("news_example", [
    pytest.param(
        {
            "feed": "feed",
            "title": "title",
            "date": "2021-01-02 01:02:03",
            "link": "link",
            "description": "description",
            "links": "links",
        }),
])
def test_file_content(tmpdir, news_storage, news_example: dict):
    """Test that the NewsStorage correctly saves and gets news in/from file.

    Args:
        tmpdir: pytest fixture
        news_storage: the NewsStorage instance
        news_example (dict): a news article example to check
    """
    tmp_file = tmpdir.join("output.txt")
    tmp_file.dump([news_example])

    news_storage.path = tmpdir.join("example.txt")
    news_storage.save_news_to_file([news_example])

    assert tmp_file.load() == news_storage.get_news_from_file()
