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


def setup_logger(destination='stdout') -> logging.Logger:
    """Sets up a logger instance of the type specified
    Args:
        destination (str, optional): The type of logger instance. Defaults to "stdout".
    Returns:
        logger : Logger instance of the type specified
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if destination == 'syslog':
        """Log messages to the syslog."""
        handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON, address='/dev/log')
        logger.addHandler(handler)
        log_format = 'python[%(process)d]: [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'
        handler.setFormatter(logging.Formatter(fmt=log_format))
    elif destination == 'stdout':
        logging.getLogger().addHandler(logging.StreamHandler())
    return logger


def valid_time(time_value):
    """Check if the input is a time in the format HHMM."""
    try:
        datetime.datetime.strptime(time_value, '%H%M')
    except ValueError:
        msg = "not a valid time: {0!r}".format(time_value)
        raise argparse.ArgumentTypeError(msg)
    return input


def get_options() -> dict:
    """Get the required options using argparse with defaults from a dotenv file.
    Returns:
        dict: A dictionary of the options to be used.
    """
    env = dotenv.dotenv_values(os.path.expanduser('~/.env'))
    parser = argparse.ArgumentParser(description='Starts and stops Zappi boost using the myenergi API.')
    parser.add_argument('-s', '--serial', help='myenergi hub serial number', default=env['myenergi_serial'])
    parser.add_argument('-p', '--password', help='myenergi password', default=env['myenergi_password'])
    parser.add_argument('-l', '--logger', help='logging mode', default='syslog', choices=['syslog', 'stdout'])
    parser.add_argument('-v', '--verbosity', help='logging verbosity', default=logging.INFO)
    parser.add_argument('-b', '--boost', required=True, choices=myenergi.ZappiBoost._member_names_,
                        help='boost action to take')
    parser.add_argument('-z', '--zappi', required=False, type=str, default=None, help='Zappi serial Number to boost')
    parser.add_argument('-k', '--kwh', required=False, default=None, type=float, help='kWh to boost')
    parser.add_argument('-t', '--time', required=False, default=None, type=valid_time,
                        help='target time for Smart Boost in format HHMM')
    args = parser.parse_args()
    if args.boost == myenergi.ZappiBoost.START.name and args.kwh is None:
        parser.error('Boost requested but kWh not provided')
    if args.boost == myenergi.ZappiBoost.START.name and args.time is not None:
        parser.error('Normal boost requested but time provided')
    if args.boost == myenergi.ZappiBoost.SMART.name and (args.kwh is None or args.time is None):
        parser.error('Smart boost requested but kWh and time not provided')
    if args.boost == myenergi.ZappiBoost.STOP.name and (args.kwh is not None or args.time is not None):
        parser.error('Stop boost requested but unnecessary kWh and time provided')
    return args


def main() -> None:
    """Set the boost mode as requested."""
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(args.verbosity)
    # Setup the local logger
    logger = setup_logger(args.logger)

    with myenergi.API(args.serial, args.password) as mye:
        if mye.get_zappi_serials() is None:
            logger.error('No Zappi Detected')
        else:
            if args.zappi is None:
                logger.info('No serial number provided. All Zappis will be boosted')
                for zappi in mye.get_zappi_serials():
                    mye.set_zappi_boost(zappi, boost=args.boost, kwh=args.kwh, boost_time=args.time)
            else:
                mye.set_zappi_boost(args.zappi, boost=args.boost, kwh=args.kwh, boost_time=args.time)


if __name__ == '__main__':
    main()
