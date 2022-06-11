"""This module provides tests for "arg_parser.py"."""

import os
import sys

import pytest

sys.path.append(os.getcwd())

from rss_parser import arg_parser


class TestLimitChecker:
    """Test "LimitChecker" class."""

    def test_init_args(self):
        """Test that "LimitChecker" doesn't change original limit value."""
        limit = "123"
        limit_checker = arg_parser.LimitChecker(limit=limit)
        assert limit is limit_checker.limit

    @pytest.mark.parametrize("limit", [
        pytest.param(
            5,
            id="positive_int",
        ),
        pytest.param(
            2.5555,
            id="positive_float",
        ),
        pytest.param(
            "2",
            id="positive_str",
        ),
        pytest.param(
            None,
            id="none",
        ),
    ])
    def test_limit_is_good(self, limit):
        """Test the "check" method using different values, which have passed the test.

        Args:
            limit: parameterized limit value to check
        """
        limit_checker = arg_parser.LimitChecker(limit=limit)
        assert limit_checker.check() is True

    @pytest.mark.parametrize("limit", [
        pytest.param(
            "-2",
            id="negative_int",
        ),
        pytest.param(
            "0",
            id="zero",
        ),
        pytest.param(
            "2.51",
            id="float",
        ),
        pytest.param(
            "a",
            id="letter",
        ),
        pytest.param(
            "None",
            id="none_str",
        ),
    ])
    def test_limit_is_bad(self, limit):
        """Test the "check" method using different values, which have not passed the test and raised "ValueError".

        Args:
            limit: parameterized limit value to check
        """
        limit_checker = arg_parser.LimitChecker(limit=limit)
        with pytest.raises(ValueError) as error:
            assert limit_checker.check() == error


class TestPageChecker:
    """Test "RssPageChecker" class."""

    @pytest.fixture
    def page(self, request):
        """Prepare "__init__".

        Args:
            request: fixture parameter, "request.param" accept url

        Returns:
            prepared instance
        """
        return arg_parser.PageChecker(url=request.param)

    @pytest.mark.parametrize(
        "page",
        [
            "https://news.yahoo.com/rss/",
            "http://feeds.bbci.co.uk/news/world/rss.xml",
        ],
        indirect=True,
    )
    def test_page_is_rss_good(self, page):
        """Test the "check" method using different urls, which have passed the test.

        Args:
            page: prepared class instance
        """
        assert page.check() is True

    @pytest.mark.parametrize(
        "page",
        [
            "https://www.python.org//",
            "https://www.google.com/",
        ],
        indirect=True,
    )
    def test_page_is_rss_bad(self, page):
        """Test the "check" method using different urls, which have not passed the test and raised "ValueError".

        Args:
            page: prepared class instance
        """
        with pytest.raises(ValueError) as error:
            assert page.check() == error

    @pytest.mark.parametrize(
        "page",
        [
            "https://py.py/",
            "https://www.123.com/",
        ],
        indirect=True,
    )
    def test_page_is_rss_connection_error(self, page):
        """Test the "check" method using different urls, which have not passed the test and raised "ConnectionError".

        Args:
            page: prepared class instance
        """
        with pytest.raises(TimeoutError) as error:
            assert page.check() == error


class TestURLChecker:
    """Test "URLChecker" class."""

    @pytest.fixture
    def page(self, request):
        """Prepare "__init__".

        Args:
            request: fixture parameter, "request.param" accept url

        Returns:
            prepared instance
        """
        return arg_parser.URLChecker(url=request.param)

    @pytest.mark.parametrize(
        "page",
        [
            "https://www.google.com/",
            "http://feeds.bbci.co.uk/news/world/rss.xml",
        ],
        indirect=True,
    )
    def test_check_url_is_available_good(self, page):
        """Test the "check" method using different urls, which have passed the test.

        Args:
            page: prepared class instance
        """
        assert page.check() is True

    @pytest.mark.parametrize(
        "page",
        [
            "httpww.google.com/",
            "news/world/rs",
        ],
        indirect=True,
    )
    def test_check_url_is_available_bad(self, page):
        """Test the "check" method using different urls, which have not passed the test and raised "ValueError".

        Args:
            page: prepared class instance
        """
        with pytest.raises(ValueError) as error:
            assert page.check() == error


class TestArgsChecker:
    """Test "ArgsChecker" class."""

    @pytest.fixture
    def page(self, request):
        """Prepare "__init__".

        Args:
            request: fixture parameter, "request.param" accept url and limit

        Returns:
            prepared instance
        """
        return arg_parser.ArgsChecker(
            url=request.param[0],
            limit=request.param[1],
            date=None,
            formats_and_paths={"EXAMPLE_FORMAT": None})

    @pytest.mark.parametrize(
        "page",
        [
            ("https://news.yahoo.com/rss/", 2, None),
            ("http://feeds.bbci.co.uk/news/world/rss.xml", 3, None),
        ],
        indirect=True,
    )
    def test_check_working_good(self, page):
        """Test the "check" method using different urls, which have passed the test.

        Args:
            page: prepared class instance
        """
        assert page.check() is True

    @pytest.mark.parametrize(
        "page",
        [
            "httpww.google.com/",
            "news/world/rs",
        ],
        indirect=True,
    )
    def test_check_working_bad(self, page):
        """Test the "check" method using different urls, which have not passed the test and raised "ValueError".

        Args:
            page: prepared class instance
        """
        with pytest.raises(ValueError) as error:
            assert page.check() == error
