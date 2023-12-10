#!/usr/bin/env python3
"""Python script to set the Zappi mode.

This script will check the current mode and then set to the desired mode if different
It will then wait until the mode has been successfully set before exiting
"""

import argparse
import logging

import myenergi
from utilities import get_env, get_logger


def get_options() -> dict:
    """Get the required options using argparse with defaults from a dotenv file.
    Returns:
        dict: A dictionary of the options to be used.
    """
    env = get_env()
    parser = argparse.ArgumentParser(description='Sets the Zappi mode using the myenergi API')
    parser.add_argument('-s', '--serial', help='myenergi hub serial number', default=(env.get('myenergi_serial')))
    parser.add_argument('-p', '--password', help='myenergi password', default=(env.get('myenergi_password')))
    parser.add_argument('-l', '--logger', help='logging mode', default='syslog', choices=['syslog', 'stdout'])
    parser.add_argument('-v', '--verbosity', help='logging verbosity', default=logging.INFO)
    parser.add_argument('-m', '--mode', help='Desired operating mode for Zappi', required=True,
                        choices=list(myenergi.ZappiMode._member_names_))
    args = parser.parse_args()
    if not args.serial or not args.password:
        parser.error("Please provide both myenergi hub serial number and password.")    
    return args


def main() -> None:
    """Set the mode for all Zappis as requested if not already set."""
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(args.verbosity)
    # Set up the local logger
    logger = get_logger(args.logger)

    with myenergi.API(args.serial, args.password) as mye:
        zappi_serials = mye.get_zappi_serials()
        if zappi_serials is None:
            logger.error("Unable to set mode as no Zappi Detected")
            exit(2)
        else:
            for serial in zappi_serials:
                mye.set_zappi_mode(serial, args.mode)


if __name__ == "__main__":
    main()
