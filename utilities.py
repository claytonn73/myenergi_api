#!/usr/bin/env python3
"""Utility functions used in various scripts."""
import logging
import logging.handlers
import os
import sys
import influxdb
from dotenv import dotenv_values


def get_logger(destination: str = "stdout"):
    """Creates a logger instance of the desired type"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if destination == "stdout":
        # Log message to sysout
        logger.addHandler(logging.StreamHandler(sys.stdout))

    elif destination == "syslog":
        # Log messages to the syslog
        handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON, 
                                                 address='/dev/log')
        logger.addHandler(handler)
        log_format = 'python[%(process)d]: [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'
        handler.setFormatter(logging.Formatter(fmt=log_format))
    return logger


def get_env() -> dict:
    """Reads environment variables from the users home directory"""
    env_path = os.path.expanduser('~/.env')
    if os.path.exists(env_path):
        env = dotenv_values(env_path)
    return env


class InfluxConnection:
    """Connect to influxdb and return connection."""

    def __init__(self, database: str, reset: bool = False):
        """Connect to influxdb."""
        try:
            self.influxdb = influxdb.InfluxDBClient(
                host='localhost', port=8086)
            if reset is True:
                self.influxdb.drop_database(database)
                self.influxdb.create_database(database)
            self.influxdb.switch_database(database)
        except (influxdb.exceptions.InfluxDBClientError, influxdb.exceptions.InfluxDBServerError) as err:
            raise SystemExit(err) from err

    def __enter__(self):
        """Return the connection."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Close connection to influxdb."""
        self.influxdb.close()
