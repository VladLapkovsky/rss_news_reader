"""This module provide logging settings.

It uses "INFO" level by default.

Use LOGGER variable to get access to logging.
"""

import logging
import sys

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

LOGGER_HANDLER = logging.StreamHandler(sys.stdout)
LOGGER_HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(LOGGER_HANDLER)
