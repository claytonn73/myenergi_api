"""Octupus energy API client ."""

import logging

from .api import API

# Import constants that are used by external users
from .const import ZappiMode, ZappiBoostOption

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
