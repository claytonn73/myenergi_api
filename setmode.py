#!/usr/bin/env python3
"""Python script to set the Zappi mode.

This script will check the current mode and then set to the desired mode if different
It will then wait until the mode has been successfully set before exiting
"""

import argparse
import logging
import logging.handlers
import time
import os

import dotenv

import myenergi


def get_logger():
    """Log messages to the syslog."""
    logger = logging.getLogger()
    handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON, address='/dev/log')
    logger.setLevel(logging.INFO)
    # logging.getLogger().addHandler(logging.StreamHandler())
    logger.addHandler(handler)
    log_format = 'python[%(process)d]: [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'
    handler.setFormatter(logging.Formatter(fmt=log_format))
    return logger


def get_options():
    """Get the required options using argparse or from a dotenv file."""
    env = dotenv.dotenv_values(os.path.expanduser("~/.env"))
    parser = argparse.ArgumentParser(description='Sets the Zappi mode using the myenergi API')
    if "myenergi_serial" not in env:
        parser.add_argument('-s', '--serial', required=True, help='myenergi hub serial number')
    if "myenergi_password" not in env:
        parser.add_argument('-p', '--password', required=True, help='myenergi password')
    parser.add_argument('-m', '--mode', required=True,
                        choices=list(myenergi.ZappiMode.values()), help='Desired operating mode for Zappi')
    args = parser.parse_args()
    if "myenergi_serial" in env:
        args.serial = env['myenergi_serial']
    if "myenergi_password" in env:
        args.password = env['myenergi_password']
    return args


def main():
    """Set the mode for all Zappis as requested if not already set."""
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(logging.INFO)
    # Set up the local logger
    logger = get_logger()
    args = get_options()

    with myenergi.API(args.serial, args.password) as mye:
        if mye.get_serials("ZAPPI") is None:
            logger.error("Unable to set mode as no Zappi Detected")
        else:
            for serial in mye.get_serials("ZAPPI"):
                current_mode = myenergi.ZappiMode[mye.get_zappi_info(serial, "MODE")]
                if args.mode == current_mode:
                    logger.info("Mode for Zappi SN: %s is already %s", serial, args.mode)
                else:
                    mye.set_zappi_mode(serial, args.mode)
                    while args.mode != myenergi.ZappiMode[mye.get_zappi_info(serial, "MODE")]:
                        time.sleep(3)
                        mye.refresh_status("ZAPPI", serial)
                    logger.info("Mode for Zappi SN:%s has been switched to %s", serial, args.mode)


if __name__ == "__main__":
    main()
