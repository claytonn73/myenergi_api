#!/usr/bin/env python3
"""Python script to start and stop Zappi boost.

The script uses argparse to parse and validate a set of input parametes
It will then set the boost mode according to the parameters passed
"""

import os
import argparse
import datetime
import logging
import logging.handlers

import dotenv

import myenergi


def get_logger():
    """Log messages to the syslog."""
    logger = logging.getLogger()
    handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON, address='/dev/log')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    log_format = 'python[%(process)d]: [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'
    handler.setFormatter(logging.Formatter(fmt=log_format))
    return logger


def valid_time(time_value):
    """Check if the input is a time in the format HHMM."""
    try:
        datetime.datetime.strptime(time_value, "%H%M")
    except ValueError:
        msg = "not a valid time: {0!r}".format(time_value)
        raise argparse.ArgumentTypeError(msg)
    return input


def get_options():
    """Get the required options using argparse or from a dotenv file."""
    env = dotenv.dotenv_values(os.path.expanduser("~/.env"))
    parser = argparse.ArgumentParser(description='Starts and stops Zappi boost using the myenergi API.')
    if "myenergi_serial" not in env:
        parser.add_argument('-s', '--serial', required=True, help='myenergi hub serial number')
    if "myenergi_password" not in env:
        parser.add_argument('-p', '--password', required=True, help='myenergi password')
    parser.add_argument('-b', '--boost', required=True,
                        choices=myenergi.ZappiBoostOption, help='boost action')
    parser.add_argument('-k', '--kwh', required=False, type=float, help='kWh to boost')
    parser.add_argument('-t', '--time', required=False, type=valid_time,
                        help='target time for Smart Boost in format HHMM')
    args = parser.parse_args()
    if args.boost == "START" and args.kwh is None:
        parser.error("Boost requested but kWh not provided")
    if args.boost == "SMART" and (args.kwh is None or args.time is None):
        parser.error("Smart boost requested but kWh and time not provided")
    if "myenergi_serial" in env:
        args.serial = env['myenergi_serial']
    if "myenergi_password" in env:
        args.password = env['myenergi_password']
    return args


def main():
    """Set the boost mode as requested."""
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(logging.INFO)
    # Setup the local logger
    logger = get_logger()
    args = get_options()
    with myenergi.API(args.serial, args.password) as mye:
        if mye.get_serials("ZAPPI") is None:
            logger.error("No Zappi Detected")
        else:
            serial = mye.get_serials("ZAPPI")[0]
            if args.boost == "START":
                mye.set_zappi_boost(serial, boost=args.boost, kwh=args.kwh)
            elif args.boost == "SMART":
                mye.set_zappi_boost(serial, boost=args.boost, kwh=args.kwh, time=args.time)
            elif args.boost == "STOP":
                mye.set_zappi_boost(serial, boost=args.boost)
            else:
                logger.error("Unknown Boost Command")


if __name__ == "__main__":
    main()
