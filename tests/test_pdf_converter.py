"""This module provides tests for "pdf_converter.py"."""

import os
import sys

import pytest

sys.path.append(os.getcwd())

from rss_parser.file_converters import pdf_converter


@pytest.fixture
def pdf_instance():
    """Prepare "__init__".

    Returns:
        prepared instance
    """
    return pdf_converter.CustomPDF()


def test_pdf_instance_file_creation(tmpdir, pdf_instance):
    """Test that the CustomPDF class creates file.

    Args:
        tmpdir: pytest fixture
        pdf_instance: the CustomPDF instance
    """
    tmp_file = tmpdir.join("output.pdf")
    pdf_instance.output(tmp_file)
    assert os.path.exists(tmp_file) is True
