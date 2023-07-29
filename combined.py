#!/usr/bin/env python3
"""Get the Zappi history and import into InfluxDB.

This script will query the first zappi found to obtain a number of days history at the hourly level
It will then import a summary of this information into an influxdb database.
"""

import asyncio
import os
import sys
import argparse
import logging
import logging.handlers
from datetime import datetime, timedelta
import dotenv
import myenergi

sys.path.append('/data/github/tesla_api/')
from tesla_api import TeslaApiClient


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
    parser.add_argument('-t', '--start', required=False, type=int, default=1, help='starting number of days ago')
    parser.add_argument('-e', '--end', required=False, type=int, default=4, help='ending number of days ago')
    parser.add_argument('-f', '--tokenfile', required=False, type=str,
                        default="~/tokens.json", help='Token file location')
    args = parser.parse_args()
    if "myenergi_serial" in env:
        args.serial = env['myenergi_serial']
    if "myenergi_password" in env:
        args.password = env['myenergi_password']
    return args


async def save_token(token, tokenfile="~/tokens.json"):
    """Save a new token file."""
    logger.info("Writing new token file")
    with open(os.path.expanduser(tokenfile), 'w') as file:
        try:
            print(os.path.expanduser(tokenfile))
            file.write(token)
        except OSError:
            logger.error("Unable to write token file")
            sys.exit(2)


def get_token(tokenfile):
    """Read the current token file."""
    try:
        token = open(os.path.expanduser(tokenfile)).read()
        return token
    except OSError:
        logger.error("Unable to read token file: {}".format(tokenfile))
        sys.exit(2)


async def main():
    """Get the Zappi history and print it."""
    # Setup the local logger
    global logger
    logger = get_logger()
    args = get_options()
    # Set the logging level for the myenergi api client
    logging.getLogger('myenergi.api').setLevel(logging.INFO)

    # Authenticate with the Powerwall
    accesstokens = get_token(args.tokenfile)
    client = TeslaApiClient(token=accesstokens, on_new_token=save_token)
    await client.authenticate()
    await client.list_products()
    energy_sites = await client.list_energy_sites()
    siteinfo = await energy_sites[0].get_energy_site_info()
    
    for daysago in range(1,7):
        pwdate = (datetime.now()-timedelta(days=daysago)).date()
        history = await energy_sites[0].get_energy_site_calendar_history_data(kind='energy', period='day', end_date = pwdate)
        pwdata = history['time_series'][0]
        date=pwdata['timestamp']
        solar_export = round(pwdata['solar_energy_exported']/1000, 2)
        grid_import = round(pwdata['grid_energy_imported']/1000, 2)
        grid_export = round(pwdata['grid_energy_exported_from_solar']/1000, 2)
        battery_import = round(pwdata['battery_energy_imported_from_grid']/1000, 2)
        battery_solar = round(pwdata['battery_energy_imported_from_solar']/1000, 2)
        house_grid = round(pwdata['consumer_energy_imported_from_grid']/1000, 2)
        house_solar = round(pwdata['consumer_energy_imported_from_solar']/1000, 2)
        house_battery = round(pwdata['consumer_energy_imported_from_battery']/1000, 2)
        print(date,grid_import, grid_export, solar_export, battery_solar, house_solar, house_battery, house_grid, battery_import)

        
    typelist = ['imp', 'exp', 'gen', 'gep', 'h1d', 'h1b', 'hom']
    total = {}

    with myenergi.API(args.serial, args.password) as mye:
        zappiserial = mye.get_serials("ZAPPI")[0]
        logger.debug("querying Zappi")
        for daysago in range(args.start, args.end):
            thetime = datetime.now()
            querytime = thetime - timedelta(days=daysago,
                                            hours=thetime.hour - 1,
                                            minutes=thetime.minute,
                                            seconds=thetime.second)
            datestring = querytime.strftime("%Y-%m-%d")

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
            total['gep'] = round(total['gep'] - total['gen'], 2)
            total['gen'] = round(total['gep'] - total['exp'] - total['h1d'], 2)
            print(datestring, total)

if __name__ == "__main__":
    asyncio.run(main())
