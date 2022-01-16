"""Module enabling the use of the myenergi API.

Provides a range of functions to enable queries and control of myenergi components
"""

import logging
import requests
import requests.auth

# import const
import myenergi.error
from myenergi.const import (
    MyEnergiEndpoint,
    MyenergiType,
    ZappiData,
    EddiData,
    HarviData,
    InternalName,
    ZappiModeParm,
    ZappiBoost,
    ZappiMode,
    ZappiStateDisplay,
    API_HEADERS,
    DIRECTOR_URL,
)

# Only export the myenergi API
__all__ = ["API"]


class API:
    """
    Class for the myenergi API.

    Args:
        serial (str): The serial number of the hub
        password (str): The password for the account
    """

    def __init__(self, serial=None, password=None):
        """Initialise the Myenergi client and perform an initial query."""
        assert serial is not None and password is not None
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialising Myenergi API Client")
        self._session = requests.Session()
        self._session.headers.update(API_HEADERS)
        self._session.auth = requests.auth.HTTPDigestAuth(serial, password)
        self._eddi = {}
        self._harvi = {}
        self._zappi = {}
        results = self._session.get(DIRECTOR_URL)
        self._url = f"https://{results.headers['X_MYENERGI-asn']}/"
        results = self._api_request(self._create_url())
        for entry in results.json():
            self._parse_api_results(entry)

    def __enter__(self):
        """Entry function for the myenergi API."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit function for the myenergi API."""
        self._session.close()

    def close(self):
        """Close the requests session."""
        self._session.close()

    def get_zappi_info(self, serial, info):
        """Return the Zappi information previously queried using the API.

        Args:
            serial (str): The serial number of the zappi
            info (str): The human-readable name of the information  to be returned
        """
        return self._zappi[serial][ZappiData[info].value]

    def get_zappi_status(self, serial):
        """Return the overall charging status of the zappi.

        Args:
            serial (str): The serial number of the zappi
        """
        self._check_serial("ZAPPI", serial)
        display_status = ZappiStateDisplay[self._zappi[serial][ZappiData["CHARGE_STATUS"].value]
                                           + str(self._zappi[serial][ZappiData["STATUS"].value])]
        return display_status

    def get_harvi_info(self, serial, info):
        """Return the Harvi information previously queried using the API.

        Args:
            serial (str): The serial number of the zappi
            info (str): The human-readable name of the information  to be returned
        """
        return self._harvi[serial][HarviData[info].value]

    def get_eddi_info(self, serial, info):
        """Return the Eddi information previously queried using the API.

        Args:
            serial (str): The serial number of the zappi
            info (str): The human-readable name of the information  to be returned
        """
        return self._eddi[serial][EddiData[info].value]

    def get_serials(self, device):
        """Return a list of serial numbers for the device type passed.

        Args:
            device (str): The type of device to return
        """
        if getattr(self, InternalName[device].value) is None:
            return None
        else:
            return list(getattr(self, InternalName[device].value).keys())

    def refresh_status(self, device, serial):
        """Refresh the information stored for a device by calling the myenergi API.

        Args:
            device (str): The type of device to return
            serial (str): The serial number of the device
        """
        self._check_serial(device, serial)
        results = self._api_request(self._create_url(endpoint=device, serial=serial))
        self._parse_api_results(results.json())

    def get_zappi_boost_times(self, serial):
        """Get the current Zappi boost times.

        Args:
            serial (str): The serial number of the zappi
        """
        self._check_serial("ZAPPI", serial)
        results = self._api_request(self._create_url(endpoint="ZAPPI_BOOST_TIME", serial=serial))
        data = results.json()
        # Only return boost slots which are populated
        self._zappi[serial][ZappiData.BOOST_TIMES.value] = []
        for slot in data.get(ZappiData.BOOST_TIMES.value):
            if slot["bdd"] != "00000000":
                self._zappi[serial][ZappiData.BOOST_TIMES.value].append(slot)

    def get_zappi_history(self, serial, history_type, date):
        """Get Zappi history of the relevant type using the Myenergi API.

        Args:
            serial (str): The serial number of the zappi
            history_type (str): Whether to get history by Minute or by Hour
            date (datetime): The date for which to obtain the history
        """
        self._check_serial("ZAPPI", serial)
        if history_type == "Minute":
            history_endpoint = "ZAPPI_HISTORY_MINUTE"
        elif history_type == "Hour":
            history_endpoint = "ZAPPI_HISTORY_HOUR"
        else:
            raise myenergi.error.ParameterError("Incorrect history type")
        results = self._api_request(self._create_url(endpoint=history_endpoint, serial=serial,
                                                     parm=f"-{str(date)}"))
        data = results.json()
        # Correct error of missing 0 hour in history
        serstring = "U" + str(serial)
        data[serstring][0]['hr'] = 0
        return data.get("U" + str(serial))

    def set_zappi_minimum_green_limit(self, serial, percentage):
        """Set the Zappi minimum green limit.

        Args:
            serial (str): The serial number of the zappi
            percentage (int): The percentage to get the minimum green limit to
        """
        self._check_serial("ZAPPI", serial)
        current = self.get_zappi_info(serial, "MINIMUM_GREEN_LIMIT")
        # set the Zappi minimum green limit as requested
        self.logger.info("Setting minimum green limit for Zappi SN: %s to %s from %s",
                         serial, percentage, current)
        self._api_request(self._create_url(endpoint="ZAPPI_MINGREEN", serial=serial,
                                           parm=f"-{str(percentage)}"))

    def set_zappi_mode(self, serial, mode):
        """Set the Zappi mode.

        Args:
            serial (str): The serial number of the zappi
            mode (str): The mode to set the Zappi to from the list in ZappiMode
        """
        self._check_serial("ZAPPI", serial)
        current = ZappiMode[self.get_zappi_info(serial, "MODE")]
        # set the Zappi mode as requested
        self.logger.info("Setting mode for Zappi SN: %s to %s from %s",
                         serial, mode, current)
        self._api_request(self._create_url(endpoint="ZAPPI_MODE", serial=serial,
                                           parm=f"{ZappiModeParm[mode].value}"))

    def set_zappi_boost(self, serial, boost="STOP", kwh="", time=""):
        """Start or stop the Zappi boost."""
        self._check_serial("ZAPPI", serial)
        # set the Zappi to boost for the desired kWh
        parm = ""
        if boost == "START":
            parm = f"{ZappiBoost[boost].value}{str(kwh)}-0000"
            self.logger.info("Starting boost for Zappi SN: %s to charge %s KwH",
                             serial, kwh)
        elif boost == "SMART":
            parm = f"{ZappiBoost[boost].value}{str(kwh)}-{str(time)}"
            self.logger.info("Starting smart boost for Zappi SN: %s to charge %s KwH by %s",
                             serial, kwh, time)
        elif boost == "STOP":
            parm = f"{ZappiBoost[boost].value}"
            self.logger.info("Stopping boost for Zappi SN: %s",
                             serial)
        self._api_request(self._create_url(endpoint="ZAPPI_MODE", serial=serial, parm=parm))

    def _api_request(self, url):
        try:
            self.logger.debug("Calling Myenergi API with URL: %s", url)
            results = self._session.get(url)
            # Check the REST API response status
            if results.status_code != requests.codes.ok:
                self.logger.error("Myenergi API returned status code: %s", results.status_code)
                results.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)
        # Then check if there is a non-zero status response provided - status is not always returned
        data = results.json()
        if MyenergiType.STATUS.value in data:
            if data.get(MyenergiType.STATUS.value) != 0:
                self.logger.error("Myenergi API returned status: %s",
                                  data.get(MyenergiType.STATUS.value))
                raise myenergi.error.ResponseError(data.get(MyenergiType.STATUS.value))
        return results

    def _create_url(self, endpoint="DEVICES", serial="", parm=""):
        url = f"{self._url}{MyEnergiEndpoint[endpoint].value}{serial}{parm}"
        return url

    def _check_serial(self, device, serial):
        if getattr(self, InternalName[device].value).get(serial) is None:
            raise myenergi.error.ParameterError("Serial number does not exist")

    def _parse_api_results(self, entry):
        for key, val in entry.items():
            if key == MyenergiType.EDDI.value:
                if len(val) > 0:
                    sno = val[0][EddiData.SERIAL_NUMBER.value]
                    self.logger.debug("Eddi data discovered with serial number: %s", sno)
                    self._eddi.update({sno: val[0]})
                else:
                    self._eddi = None
            elif key == MyenergiType.HARVI.value:
                if len(val) > 0:
                    sno = val[0][HarviData.SERIAL_NUMBER.value]
                    self.logger.debug("Harvi data discovered with serial number: %s", sno)
                    self._harvi.update({sno: val[0]})
                else:
                    self._harvi = None
            elif key == MyenergiType.ZAPPI.value:
                if len(val) > 0:
                    sno = val[0][ZappiData.SERIAL_NUMBER.value]
                    self.logger.debug("Zappi data discovered with serial number: %s", sno)
                    self._zappi.update({sno: val[0]})
                else:
                    self._zappi = None
            elif key == MyenergiType.URL.value:
                self._url = f"https://{val}/"
            elif key == MyenergiType.FIRMWARE.value:
                self._firmware = val
            else:
                self.logger.error("Unknown api results returned: key= %s value= %s", key, val)
