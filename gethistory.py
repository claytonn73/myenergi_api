#!/usr/bin/env python3
"""Get the Zappi history and import into InfluxDB.

This script will query the first zappi found to obtain a number of days history at the hourly level
It will then import a summary of this information into an influxdb database.
"""

import argparse
import logging
import logging.handlers
from datetime import datetime, timedelta

import myenergi
from utilities import InfluxConnection, get_env, get_logger


def get_options() -> dict:
    """Get the required options using argparse or from a dotenv file."""
    env = get_env()
    parser = argparse.ArgumentParser(description='Gets history from the Zappi and imports to influxdb.')
    parser.add_argument('-s', '--serial', help='myenergi hub serial number', default=(env.get('myenergi_serial')))
    parser.add_argument('-p', '--password', help='myenergi password', default=(env.get('myenergi_password')))
    parser.add_argument('-t', '--start', required=False, type=int, default=1, help='starting number of days ago')
    parser.add_argument('-e', '--end', required=False, type=int, default=4, help='ending number of days ago')
    parser.add_argument('-l', '--logger', help='logging mode', default='syslog', choices=['syslog', 'stdout'])
    parser.add_argument('-v', '--verbosity', help='logging verbosity', default=logging.INFO)
    args = parser.parse_args()
    return args


def main() -> None:
    """Get the Zappi history and import into InfluxDB."""
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(args.verbosity)
    # Setup the local logger
    logger = get_logger(args.logger)

    with InfluxConnection(database="myenergi", reset=False) as connection:
        with myenergi.API(args.serial, args.password) as mye:
            # If no zappi detected then exit
            zappilist = mye.get_serials(myenergi.MyenergiType.ZAPPI) 
            if zappilist is None:
                logger.error("Unable to get history as no Zappi Detected")
            else:
                # For each zappi detected for the account
                for zappiserial in zappilist:
                    logger.info(f"Adding Myenergi information to influxdb for Zappi S/N: {zappiserial}")
                    starttime = datetime.now() - timedelta(days=args.start)
                    datestring = starttime.strftime("%Y-%m-%d")
                    history = mye.get_zappi_daily_total(zappiserial, datestring, args.end)
                    influx_data = []
                    for entry in history.history_data:
                        # Create data for influxdb and write to database
                        influx_tags = {
                            'serial_number': zappiserial
                        }
                        influx_fields = {
                            'zappi_diverted': float(getattr(entry, myenergi.ZappiStats.ZAPPI_DIVERTED.value)),
                            'zappi_imported': float(getattr(entry, myenergi.ZappiStats.ZAPPI_IMPORTED.value)),
                            'home_solar': float(getattr(entry, myenergi.ZappiStats.HOME_SOLAR.value)),
                            'home_grid': float(getattr(entry, myenergi.ZappiStats.HOME_GRID.value)),
                            'solar_generated': float(getattr(entry, myenergi.ZappiStats.SOLAR_GENERATED.value)),
                            'solar_used': float(getattr(entry, myenergi.ZappiStats.SOLAR_USED.value)),
                            'grid_imported': float(getattr(entry, myenergi.ZappiStats.GRID_IMPORTED.value)),
                            'grid_exported': float(getattr(entry, myenergi.ZappiStats.GRID_EXPORTED.value)),
                            'month': datetime.strftime(getattr(entry, "timestamp"), "%b %Y"),
                        }
                        influx_data.append(
                            {
                                'measurement':  "zappi_daily_energy",
                                'time': datetime.strftime(getattr(entry, "timestamp"), "%Y-%m-%dT%H:%M"),
                                'tags': influx_tags,
                                'fields': influx_fields,
                            }
                        )
                    connection.influxdb.write_points(influx_data)


if __name__ == "__main__":
    main()
