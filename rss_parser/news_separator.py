"""This module provides a single function for more human readable output."""

import os


def separate_news(separator_symbol: str = "-", separator_len: int = 100):
    """Return "separator_symbol" multiplied on terminal size (if possible to get terminal size) or on 100.

    Args:
        separator_symbol (str): "-" by default
        separator_len (int): set the number of "separator_symbol"


    Returns:
        "separator_symbol" multiplied on terminal size or on 100
    """
    try:
        return separator_symbol * os.get_terminal_size().columns
    except OSError:
        return separator_symbol * separator_len
