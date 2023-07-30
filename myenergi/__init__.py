"""Myenergi API client ."""

import logging

from .api import API  # noqa: F401
# Import constants that are used by external users

from .const import ZappiMode, ZappiBoost, History, ZappiStats, MyenergiType  # noqa: F401

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
