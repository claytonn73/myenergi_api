"""This is a Python module that enables the use of the myenergi API.
This API is provided by the company "myenergi" for querying and controlling their energy-related components,
such as Zappi, Eddi, Harvi, and Libbi devices.

The code defines a class named "API" that provides various methods to interact with the myenergi API.

The class contains several methods to retrieve specific information about the connected devices, such as
get_zappi_info, get_harvi_info, and get_eddi_info.

There are also methods to refresh the status of a device, set various configurations (e.g., set_zappi_mode,
set_zappi_boost).

It is also possible to retrieve historical data from the zappi.

Helper Methods: There are internal helper methods such as _api_request for making API calls, _create_url
for constructing the API URLs, and _check_serial for validating device serial numbers.
"""

import time
import logging
import requests
import requests.auth
import json
from datetime import datetime, timedelta

import myenergi.error
from myenergi.const import (
    MyEnergiEndpoint,
    MyenergiType,
    ZappiData,
    EddiData,
    HarviData,
    LibbiData,
    ZappiModeParm,
    ZappiBoost,
    ZappiMode,
    History,
    EddiMode,
    ZappiStateDisplay,

)

# Only export the myenergi API
__all__ = ["API"]


class API:
    """
    A Python module that enables the use of the myenergi API.

    Args:
        serial (str): The serial number of the hub
        password (str): The password for the account
    """

    def __init__(self, serial: str = None, password: str = None) -> None:
        """Initialise the Myenergi client and perform an initial query.

        Args:
            serial (str, optional): Serial number of the myenergi hub. Defaults to None.
            password (str, optional): password for the myenergi hub. Defaults to None.
        """
        assert serial is not None and password is not None
        # Setup a logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialising Myenergi API Client for hub:{serial}")
        # Create a session for the API requests
        self._session = requests.Session()
        self._session.headers.update(MyEnergiEndpoint.API_HEADERS.value)
        self._session.auth = requests.auth.HTTPDigestAuth(serial, password)
        # Call the director URL to get the URL for this hub which is returned in a header field
        results = self._session.get(MyEnergiEndpoint.DIRECTOR_URL.value)
        self._url = f"https://{results.headers[MyEnergiEndpoint.ASN_HEADER_FIELD.value]}/"
        # Perform an initial query to the hub to get the list of devices and their attributes
        results = self._api_request(self._create_url())
        self._devices = myenergi.const.devices()
        for entry in results:
            self._parse_api_results(entry)
        # Get the boost times for all Zappis
        for serial in self.get_zappi_serials():
            self._get_zappi_boost_times(serial)
        # Get the boost times for all Eddis
        for serial in self.get_serials(MyenergiType.EDDI):
            self._get_eddi_boost_times(serial)

    def __enter__(self) -> "API":
        """Entry function for the myenergi API."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """Exit function for the myenergi API."""
        self._session.close()

    def close(self) -> None:
        """Close the requests session."""
        self._session.close()

    def get_zappi_info(self, serial: int, info: ZappiData) -> str:
        """Return the Zappi information previously queried using the API.

        Args:
            serial (int): The serial number of the zappi
            info (ZappiData): The human-readable name of the information  to be returned
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        return getattr(self._devices.zappi[serial], info.value)

    def get_zappi_status(self, serial: int) -> str:
        """Return the overall charging status of the zappi.

        Args:
            serial (int): The serial number of the zappi
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        myzappi = self._devices.zappi[serial]
        display_status = ZappiStateDisplay[getattr(myzappi, ZappiData.CHARGE_STATUS.value)
                                           + str(getattr(myzappi, ZappiData.STATUS.value))].value
        return display_status

    def get_harvi_info(self, serial: int, info: HarviData) -> str:
        """Return the Harvi information previously queried using the API.

        Args:
            serial (int): The serial number of the harvi
            info (HarviData): The human-readable name of the information  to be returned
        """
        self._check_serial(MyenergiType.HARVI, serial)
        return getattr(self._devices.harvi[serial], info.value)

    def get_eddi_info(self, serial: int, info: EddiData) -> str:
        """Return the Eddi information previously queried using the API.

        Args:
            serial (int): The serial number of the eddi
            info (EddiData): The human-readable name of the information  to be returned
        """
        self._check_serial(MyenergiType.EDDI, serial)
        return getattr(self._devices.eddi[serial], info.value)

    def get_serials(self, device: MyenergiType) -> list:
        """Return a list of serial numbers for the device type passed.

        Args:
            device (MyenergiType): The type of device to return
        """
        if getattr(self._devices, device.value) is not None:
            return getattr(self._devices, device.value).keys()
        else:
            return []

    def get_zappi_serials(self) -> list:
        """Return a list of serial numbers for the device type passed.

        Args:
            device (str): The type of device to return
        """
        if getattr(self._devices, MyenergiType.ZAPPI.value) is not None:
            return getattr(self._devices, MyenergiType.ZAPPI.value).keys()
        else:
            return []

    def refresh_status(self, device: MyenergiType, serial: int) -> None:
        """Refresh the information stored for a device by calling the myenergi API.

        Args:
            device (str): The type of device to return
            serial (int): The serial number of the device
        """
        self._check_serial(device, serial)
        results = self._api_request(self._create_url(endpoint=MyEnergiEndpoint[device.name], serial=serial))
        self._parse_api_results(results)
        if device == MyenergiType.ZAPPI:
            self._get_zappi_boost_times(serial)
        if device == MyenergiType.EDDI:
            self._get_eddi_boost_times(serial)

    def _get_eddi_boost_times(self, serial: int) -> None:
        """Get the current Eddi boost times.

        Args:
            serial (int): The serial number of the Eddi
        """
        self._check_serial(MyenergiType.EDDI, serial)
        results = self._api_request(self._create_url(endpoint=MyEnergiEndpoint.EDDI_BOOST_TIME, serial=serial))
        boost = myenergi.const.boosttimes(**results)
        self._devices.eddi[serial].boost_times = boost.boost_times

    def _get_zappi_boost_times(self, serial: int) -> None:
        """Get the current Zappi boost times.

        Args:
            serial (int): The serial number of the zappi
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        results = self._api_request(self._create_url(endpoint=MyEnergiEndpoint.ZAPPI_BOOST_TIME, serial=serial))
        boost = myenergi.const.boosttimes(**results)
        self._devices.zappi[serial].boost_times = boost.boost_times

    def get_zappi_daily_total(self, serial: int, date: str, querydays: int = 1) -> myenergi.const.daily_history:
        """Get the daily total history information for the date and serial provided
        Args:
            serial (int): The serial number of the zappi
            date (datetime): The date for which to obtain the history
            querydays (int): The number of days to query counting back from today
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        daily_history = myenergi.const.daily_history(serial)
        thedate = datetime.strptime(date, "%Y-%m-%d")
        for day in range(querydays-1):
            today = thedate - timedelta(days=day)
            history = self.get_zappi_history(serial, History.HOUR, datetime.strftime(today, "%Y-%m-%d"))
            summary_data = myenergi.const.daily_data(today)
            for data in history.history_data:
                for stat in myenergi.const.ZappiStats:
                    setattr(summary_data, stat.value, round(getattr(summary_data, stat.value) +
                                                            getattr(data, stat.value), 2))
            daily_history.history_data.append(summary_data)
        return daily_history

    def get_eddi_history(self, serial: int, history_type: History, date: str) -> myenergi.const.hourly_history:
        """Get Eddi history of the relevant type using the Myenergi API.

        Args:
            serial (int): The serial number of the eddi
            history_type (str): Whether to get history by Minute or by Hour
            date (datetime): The date for which to obtain the history
        """
        self._check_serial(MyenergiType.EDDI, serial)
        results = self._api_request(self._create_url(endpoint=MyEnergiEndpoint[history_type.value], serial=serial,
                                                     parm=f"-{str(date)}"))
        serstring = "U" + str(serial)
        if history_type == History.MINUTE:
            myhistory = myenergi.const.minute_history(serial)
            for entry in results[serstring]:
                myhistory.history_data.append(myenergi.const.minute_data(**entry))
        elif history_type == History.HOUR:
            myhistory = myenergi.const.hourly_history(serial)
            for entry in results[serstring]:
                myhistory.history_data.append(myenergi.const.hourly_data(**entry))
        return myhistory

    def get_zappi_history(self, serial: int, history_type: History, date: str) -> myenergi.const.hourly_history:
        """Get Zappi history of the relevant type using the Myenergi API.

        Args:
            serial (int): The serial number of the zappi
            history_type (str): Whether to get history by Minute or by Hour
            date (datetime): The date for which to obtain the history
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        results = self._api_request(self._create_url(endpoint=MyEnergiEndpoint[history_type.value], serial=serial,
                                                     parm=f"-{str(date)}"))
        serstring = "U" + str(serial)
        if history_type == History.MINUTE:
            myhistory = myenergi.const.minute_history(serial)
            for entry in results[serstring]:
                myhistory.history_data.append(myenergi.const.minute_data(**entry))
        elif history_type == History.HOUR:
            myhistory = myenergi.const.hourly_history(serial)
            for entry in results[serstring]:
                myhistory.history_data.append(myenergi.const.hourly_data(**entry))
        return myhistory

    def set_zappi_minimum_green_limit(self, serial: int, percentage: int) -> None:
        """Set the Zappi minimum green limit.

        Args:
            serial (int): The serial number of the zappi
            percentage (int): The percentage to get the minimum green limit to
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        current_percentage = self.get_zappi_info(serial, ZappiData.MINIMUM_GREEN_LIMIT)
        if percentage == current_percentage:
            self.logger.info(f"Minimum green limit for Zappi SN: {serial} is already {percentage}")
        else:
            # set the Zappi minimum green limit as requested
            self.logger.info(f"Setting minimum green limit for Zappi SN:"
                             f"{serial} to {percentage} from {current_percentage}")
            self._api_request(self._create_url(endpoint=MyEnergiEndpoint.ZAPPI_MINGREEN, serial=serial,
                                               parm=f"-{str(percentage)}"))
            while percentage != self.get_zappi_info(serial, ZappiData.MINIMUM_GREEN_LIMIT):
                time.sleep(3)
                self.refresh_status(MyenergiType.ZAPPI, serial)
            self.logger.info(f"Minimum green limit for Zappi SN:{serial} has been switched to {percentage}")

    def set_eddi_mode(self, serial: int, mode: EddiMode) -> None:
        """Set the Zappi mode and wait until the mode has changed

        Args:
            serial (int): The serial number of the Eddi
            mode (ZappiMode): The mode to set the Eddi to from the list in ZappiMode
        """
        self._check_serial(MyenergiType.EDDI, serial)
        self.logger.info(f"Setting mode for Eddi SN: {serial} to {mode.name}")
        self._api_request(self._create_url(endpoint=MyEnergiEndpoint.EDDI_MODE, serial=serial,
                                           parm=f"{mode.value}"))

    def set_zappi_mode(self, serial: int, mode: ZappiMode) -> None:
        """Set the Zappi mode and wait until the mode has changed

        Args:
            serial (int): The serial number of the zappi
            mode (ZappiMode): The mode to set the Zappi to from the list in ZappiMode
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        current_mode = self.get_zappi_info(serial, ZappiData.MODE)
        if ZappiMode[mode].value == current_mode:
            self.logger.info(f"Mode for Zappi SN: {serial} is already {mode}")
        else:
            # set the Zappi mode as requested
            self.logger.info(f"Setting mode for Zappi SN: {serial} to {mode} from {ZappiMode(current_mode).name}")
            self._api_request(self._create_url(endpoint=MyEnergiEndpoint.ZAPPI_MODE, serial=serial,
                                               parm=f"{ZappiModeParm[mode].value}"))
            start_time = time.monotonic()
            while ZappiMode[mode].value != self.get_zappi_info(serial, ZappiData.MODE):
                time.sleep(3)
                self.refresh_status(MyenergiType.ZAPPI, serial)
                if time.monotonic() > (start_time + 60):
                    raise myenergi.error.TimeoutError(f"Timed out waiting for mode for Zappi SN:{serial} to switch")
            self.logger.info(f"Mode for Zappi SN:{serial} has been switched to {mode}")

    def set_eddi_boost(self, serial: int, heater: int = 1, boost_time: int = 0) -> None:
        """Start or stop the Eddi boost.

        Args:
            serial (int): Serial number of the Zappi to boost - or all will be boosted
            heater (int) : Number of the heater to boost
            boost_time (int, optional): time for boost. Defaults to 0 which cancels boost
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        # set the Zappi to boost for the desired kWh
        if boost_time == 0:
            parm = f"-1-{heater}-{boost_time}"
            self.logger.info(f"Stopping boost for Eddi SN: {serial}")
        else:
            parm = f"-10-{heater}-{boost_time}"
            self.logger.info(f"Starting boost for Eddi SN:{serial} for {boost_time} minutes")
        self._api_request(self._create_url(endpoint=MyEnergiEndpoint.EDDI_BOOST, serial=serial, parm=parm))

    def set_zappi_boost(self, serial: int, boost: ZappiBoost = ZappiBoost.STOP,
                        kwh: int = 0, boost_time: str = None) -> None:
        """Start or stop the Zappi boost.

        Args:
            serial (int): Serial number of the Zappi to boost - or all will be boosted
            boost (ZappiBoost, optional): Start, Stop or Smart boost. Defaults to ZappiBoost.STOP.
            kwh (int, optional): kwn to boost. Defaults to 0.
            boost_time (int, optional): time for smart boost. Defaults to None.
        """
        self._check_serial(MyenergiType.ZAPPI, serial)
        # set the Zappi to boost for the desired kWh
        if boost == ZappiBoost.START.name:
            if kwh == 0:
                raise myenergi.error.ParameterError("START boost specified without required values")
            else:
                parm = f"{ZappiBoost[boost].value}{str(kwh)}-0000"
                self.logger.info(f"Starting boost for Zappi SN:{serial} to charge {kwh} kWh")
        elif boost == ZappiBoost.SMART.name:
            if (kwh == 0) or (boost_time is None):
                raise myenergi.error.ParameterError("SMART boost specified without required values")
            else:
                parm = f"{ZappiBoost[boost].value}{str(kwh)}-{str(boost_time)}"
                self.logger.info(f"Starting smart boost for Zappi SN: {serial} to charge {kwh} kWh by {boost_time}")
        elif boost == ZappiBoost.STOP.name:
            parm = f"{ZappiBoost[boost].value}"
            self.logger.info(f"Stopping boost for Zappi SN: {serial}")
        self._api_request(self._create_url(endpoint=MyEnergiEndpoint.ZAPPI_MODE, serial=serial, parm=parm))

    def _api_request(self, url: str) -> json:
        """Call the REST API with the passed URL and check the response before returning the JSON results.
        Args:
            url (str): URL to be passed to the REST API
        Returns:
            json: The json returned by the REST API
        """
        try:
            self.logger.debug(f"Calling Myenergi API with URL: {url}")
            results = self._session.get(url)
            # Check the REST API response status
            if results.status_code != requests.codes.ok:
                self.logger.error(f"Myenergi API returned status code: {results.status_code}")
                results.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.close()
            raise SystemExit(err)
        except requests.exceptions.RequestException as err:
            self.close()
            raise SystemExit(err)
        # Get the JSON data from the results of the API call.
        data = results.json()
        self.logger.debug(f"Formatted API results:\n {json.dumps(data, indent=2)}")
        # Then check if there is a non-zero status response provided - status is not always returned
        if MyenergiType.STATUS.value in data:
            if data.get(MyenergiType.STATUS.value) != 0:
                self.logger.error(f"Myenergi API returned status: {data.get(MyenergiType.STATUS.value)}")
                self.close()
                raise myenergi.error.ResponseError(data.get(MyenergiType.STATUS.value))
        return data

    def _create_url(self, serial: str = "", parm: str = "",
                    endpoint: MyEnergiEndpoint = MyEnergiEndpoint.DEVICES) -> str:
        """Create a URL for use with the myenergi API
        Args:
            endpoint (MyEnergiEndpoint, optional): The REST API endoing to call. Defaults to MyEnergiEndpoint.DEVICES.
            serial (str): Serial number to be used for the API call.
            parm (str, optional): Parameter string to be added to the API URL. Defaults to "".
        Returns:
            str: The URL to be used
        """
        url = f"{self._url}{endpoint.value}{serial}{parm}"
        return url

    def _check_serial(self, device: MyenergiType, serial: str) -> None:
        """Check whether the serial number exists and is the type of device specified.
        Args:
            device (MyenergiType): The type of device to look for
            serial (str): the serial number to look for
        """
        for key in getattr(self._devices, device.value).keys():
            if str(key) == str(serial):
                return
        raise myenergi.error.ParameterError("Serial number does not exist")

    def _parse_api_results(self, entry: json) -> None:
        """Parses the output of an API call that provides information about myenergi devices
        The output is loaded into dataclass instances for the different device types
        which will validate the data received and create a default for missing values

        Args:
            entry (json): Output from the myenergi API providing device information
        """
        for key, val in entry.items():
            if key == MyenergiType.EDDI.value:
                if val:
                    for device in val:
                        sno = device[EddiData.SERIAL_NUMBER.value]
                        self.logger.debug(f"Eddi data discovered with serial number: {sno}")
                        self._devices.eddi.update({sno: myenergi.const.eddi(**device)})
                else:
                    self._devices.eddi = None
            elif key == MyenergiType.HARVI.value:
                if val:
                    for device in val:
                        sno = device[HarviData.SERIAL_NUMBER.value]
                        self.logger.debug(f"Harvi data discovered with serial number: {sno}")
                        self._devices.harvi.update({sno: myenergi.const.harvi(**device)})
                else:
                    self._devices.harvi = None
            elif key == MyenergiType.LIBBI.value:
                if val:
                    for device in val:
                        sno = device[LibbiData.SERIAL_NUMBER.value]
                        self.logger.debug(f"Libbi data discovered with serial number: {sno}")
                        self._devices.libbi.update({sno: myenergi.const.libbi(**device)})
                else:
                    self._devices.libbi = None
            elif key == MyenergiType.ZAPPI.value:
                if val:
                    for device in val:
                        sno = device[ZappiData.SERIAL_NUMBER.value]
                        self.logger.debug(f"Zappi data discovered with serial number: {sno}")
                        self._devices.zappi.update({sno: myenergi.const.zappi(**device)})
                else:
                    self._devices.zappi = None
            elif key == MyenergiType.URL.value:
                self._url = f"https://{val}/"
                self._devices.asn = val
            elif key == MyenergiType.FIRMWARE.value:
                self._devices.fwv = val
            else:
                self.logger.error(f"Unknown api results returned: key= {key} value= {val}")
