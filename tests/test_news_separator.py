"""This module provides tests for "news_separator.py"."""

import os
import sys

sys.path.append(os.getcwd())

from rss_parser.news_separator import separate_news


def test_separate_news():
    """Test result of the "separate_news" function."""
    sym = "*"
    assert len(sym * 120) == len(separate_news(separator_len=120))
