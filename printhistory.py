#!/usr/bin/env python3
"""Get the Zappi history and import into InfluxDB.

This script will query the first zappi found to obtain a number of days history at the hourly level
It will then import a summary of this information into an influxdb database.
"""

import os
import sys
import argparse
import logging
import logging.handlers
from datetime import datetime

import dotenv

import myenergi


def get_logger():
    """Log message to sysout."""
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    return logger


def get_options():
    """Get the required options using argparse or from a dotenv file."""
    env = dotenv.dotenv_values(os.path.expanduser("~/.env"))
    parser = argparse.ArgumentParser(description='Gets history from the Zappi and imports to influxdb.')
    if "myenergi_serial" not in env:
        parser.add_argument('-s', '--serial', required=True, help='myenergi hub serial number')
    if "myenergi_password" not in env:
        parser.add_argument('-p', '--password', required=True, help='myenergi password')
    parser.add_argument('-t', '--start', required=False, type=int, default=1, help='starting number of days ago')
    parser.add_argument('-e', '--end', required=False, type=int, default=4, help='ending number of days ago')
    args = parser.parse_args()
    if "myenergi_serial" in env:
        args.serial = env['myenergi_serial']
    if "myenergi_password" in env:
        args.password = env['myenergi_password']
    return args


def main():
    """Get the Zappi history and print it."""
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(logging.INFO)

    # Setup the local logger
    logger = get_logger()

    with myenergi.API(args.serial, args.password) as mye:
        zappiserials = mye.get_serials(myenergi.const.MyenergiType.ZAPPI)
        for serial in zappiserials:
            logger.info("querying Zappi: %s", serial)
            thetime = datetime.now()
            datestring = thetime.strftime("%Y-%m-%d")
            days = 7
            history = mye.get_zappi_daily_total(serial, datestring, days)
            for entry in history.history_data:
                print(entry)
            exit(0)


if __name__ == "__main__":
    main()
