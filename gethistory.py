#!/usr/bin/env python3
"""Get the Zappi history and import into InfluxDB.

This script will query the first zappi found to obtain a number of days history at the hourly level
It will then import a summary of this information into an influxdb database.
"""

import os
import argparse
import logging
import logging.handlers
from datetime import datetime, timedelta

import dotenv
import influxdb

import myenergi


def get_logger():
    """Log messages to the syslog."""
    logger = logging.getLogger()
    handler = logging.handlers.SysLogHandler(facility=logging.handlers.SysLogHandler.LOG_DAEMON,
                                             address='/dev/log')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    log_format = 'python[%(process)d]: [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d \"%(message)s\"'
    handler.setFormatter(logging.Formatter(fmt=log_format))
    return logger


def get_options():
    """Get the required options using argparse or from a dotenv file."""
    env = dotenv.dotenv_values(os.path.expanduser("~/.env"))
    parser = argparse.ArgumentParser(description='Gets history from the Zappi and imports to influxdb.')
    if "myenergi_serial" not in env:
        parser.add_argument('-s', '--serial', required=True, help='myenergi hub serial number')
    if "myenergi_password" not in env:
        parser.add_argument('-p', '--password', required=True, help='myenergi password')
    parser.add_argument('-s', '--start', required=False, type=int, default=1, help='starting number of days ago')
    parser.add_argument('-e', '--end', required=False, type=int, default=4, help='ending number of days ago')
    args = parser.parse_args()
    if "myenergi_serial" in env:
        args.serial = env['myenergi_serial']
    if "myenergi_password" in env:
        args.password = env['myenergi_password']
    return args


def main():
    """Get the Zappi history and import into InfluxDB."""
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(logging.INFO)
    # Setup the local logger
    logger = get_logger()
    my_influxdb = influxdb.InfluxDBClient(host='localhost', port=8086)
    # influxdb.drop_database('myenergi')
    # influxdb.create_database('myenergi')
    my_influxdb.switch_database('myenergi')

    typelist = ['imp', 'exp', 'gen', 'gep', 'h1d', 'h1b', 'hom']
    total = {}
    logger.info("Adding Myenergi information to influxdb")
    with myenergi.API(args.serial, args.password) as mye:
        zappiserial = mye.get_serials("ZAPPI")[0]
        for daysago in range(args.start, args.end):
            thetime = datetime.now()
            querytime = thetime - timedelta(days=daysago,
                                            hours=thetime.hour - 1,
                                            minutes=thetime.minute,
                                            seconds=thetime.second)
            datestring = querytime.strftime("%Y-%m-%d")
            datetimestring = querytime.strftime("%Y-%m-%dT%H:%M")

            result = mye.get_zappi_history(zappiserial, "Hour", datestring)
            for key in typelist:
                total[key] = 0
            for entry in result:
                for key in typelist:
                    if key in entry.keys():
                        entry[key] = round(entry[key] / 3600 / 1000, 2)
                        total[key] = round(total[key] + entry[key], 2)
                    else:
                        entry[key] = 0
            total['hom'] = round(total['gep'] + total['imp']
                                 - total['exp'] - total['h1d'] - total['gen'] - total['h1b'], 2)
            print(datestring, total)

            # Create data for influxdb and write to database
            influx_tags = {
                'serial_number': zappiserial
            }
            influx_fields = {
                'zappi_diverted': float(total['h1d']),
                'zappi_imported': float(total['h1b']),
                'home_used': float(total['hom']),
                'solar_generated': float(total['gep']),
                'solar_used': float(total['gen']),
                'grid_imported': float(total['imp']),
                'grid_exported': float(total['exp']),
                'month': querytime.strftime("%b %Y"),
            }
            influx_data = [
                {
                    'measurement':  "zappi_daily_energy",
                    'time': datetimestring,
                    'tags': influx_tags,
                    'fields': influx_fields,
                }
            ]
            my_influxdb.write_points(influx_data)


if __name__ == "__main__":
    main()
