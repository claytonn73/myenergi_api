"""Provide constants used by the myenergi API."""

from enum import Enum

MYENERGI_DIRECTOR_URL = "https://director.myenergi.net"
MYENERGI_API_HEADERS = {'user-agent': 'python/0.0.1'}
MYENERGI_API_STATUS = "status"
MYENERGI_API_BOOST_TIMES = "boost_times"


class MyEnergiEndpoint(Enum):
    """Supported endpoints for the Myenergi API."""

    DEVICES = "cgi-jstatus-*"
    HARVI = "cgi-jstatus-H"
    ZAPPI = "cgi-jstatus-Z"
    ZAPPI_MODE = "cgi-zappi-mode-Z"
    ZAPPI_MINGREEN = "cgi-set-min-green-Z"
    ZAPPI_BOOST_TIME = "cgi-boost-time-Z"
    ZAPPI_HISTORY_MINUTE = "cgi-jday-Z"
    ZAPPI_HISTORY_HOUR = "cgi-jdayhour-Z"
    EDDI = "cgi-jstatus-E"
    EDDI_PRIORITY = "cgi-set-heater-priority-E"
    EDDI_HISTORY_DAY = "cgi-jday-E"
    EDDI_BOOST_TIME = "cgi-boost-time-E"
    EDDI_BOOST = "cgi-eddi-boost-E"


class MyenergiType(Enum):
    """Supported Device Types and other Responses."""

    HARVI = "harvi"
    EDDI = "eddi"
    ZAPPI = "zappi"
    URL = "asn"
    FIRMWARE = "fwv"


class ZappiData(Enum):
    """Data returned for the Zappi."""

    DATE = "dat"
    TIME = "time"
    SERIAL_NUMBER = "sno"
    FREQUENCY = "frq"
    VOLTAGE = "vol"
    CHARGE_STATUS = "pst"
    MODE = "zmo"
    STATUS = "sta"
    MINIMUM_GREEN_LIMIT = "mgl"
    CHARGE_ADDED = "che"
    DIVERTED_WATTS = "div"
    GENERATED_WATTS = "gen"
    GRID_WATTS = "grd"
    PHASE = "pha"
    FIRMWARE_VERSION = "fwv"
    LOCK = "lck"
    CT1_NAME = "ectt1"
    CT2_NAME = "ectt2"
    CT3_NAME = "ectt3"
    CT4_NAME = "ectt4"
    CT5_NAME = "ectt5"
    CT6_NAME = "ectt6"
    CT1_WATTS = "ectp1"
    CT2_WATTS = "ectp2"
    CT3_WATTS = "ectp3"
    CT4_WATTS = "ectp4"
    HISTORY = "history"
    BOOST_TIMES = "boost_times"


class ZappiModeParm(Enum):
    """API paramemters to set different Zappi modes."""

    FAST = "-1-0-0-0000"
    ECO = "-2-0-0-0000"
    ECO_PLUS = "-3-0-0-0000"
    STOP = "-4-0-0-0000"


ZappiMode = {
    1: "FAST",
    2: "ECO",
    3: "ECO_PLUS",
    4: "STOP"
}


ZappiState = {
    0: "Starting",
    1: "Paused",
    2: "Demand Side Response",
    3: "Charging",
    4: "Boosting",
    5: "Charge Complete"
}


ZappiStatus = {
    "A": "EV Disconnected",
    "B1": "EV Connected",
    "B2": "Waiting for EV",
    "C1": "EV Ready to Charge",
    "C2": "Charging",
    "F": "Fault"
}


ZappiStateDisplay = {
    "A1": "EV Disconnected",
    "A2": "EV Disconnected",
    "A3": "EV Disconnected",
    "A4": "EV Disconnected",
    "A5": "EV Disconnected",
    "B11": "Waiting for surplus power",
    "B12": "Waiting for surplus power",
    "B14": "Waiting for EV",
    "B15": "Charge Complete",
    "B21": "Charge Delayed",
    "B22": "Charge Delayed",
    "B24": "Charge Delayed",
    "B25": "Charge Complete",
    "C11": "Waiting for surplus power",
    "C12": "Waiting for surplus power",
    "C14": "Boosting",
    "C15": "Charge Complete",
    "C21": "Charging",
    "C22": "Charging",
    "C23": "Charging",
    "C24": "Boosting",
    "F1": "Fault/Restart",
    "F2": "Fault/Restart",
    "F3": "Fault/Restart",
    "F4": "Fault/Restart",
    "F5": "Fault/Restart"
}


ZappiHistoryOption = {
    "Minute", "Hour"
}


class ZappiBoost(Enum):
    """API paramemters to control boosting of the Zappi."""

    START = "-0-10-"
    SMART = "-0-11-"
    STOP = "-0-2-0-0000"


ZappiBoostOption = {
    "START", "SMART", "STOP"
}


class EddiData(Enum):
    """Data returned for the Eddi."""

    DATE = "dat"
    TIME = "time"
    SERIAL_NUMBER = "sno"
    FREQUENCY = "frq"
    VOLTAGE = "vol"
    GENERATED_WATTS = "gen"
    GRID_WATTS = "grd"


class HarviData(Enum):
    """Data returned for the Harvi."""

    DATE = "dat"
    TIME = "time"
    SERIAL_NUMBER = "sno"
    FIRMWARE_VERSION = "fwv"
    CT1_NAME = "ectt1"
    CT2_NAME = "ectt2"
    CT3_NAME = "ectt3"
    CT1_WATTS = "ectp1"
    CT2_WATTS = "ectp2"
    CT3_WATTS = "ectp3"
    CT1_PHASE = "ect1p"
    CT2_PHASE = "ect2p"
    CT3_PHASE = "ect3p"


class LoadTypes(Enum):
    """Text values for different load types in Zappi and Harvi API responses."""

    GENERATION = "Generation"
    GRID = "Grid"
    BATTERY = "AC Battery"
    SOLAR = "Solar"
    INTERNAL = "Internal Load"
    NONE = "None"


MyEnergiResponse = {
    0: "Success",
    -1: "Invalid ID",
    -2: "Invalid DSR command sequence number",
    -3: "No action taken. Command Sequence number is same as last.",
    -4: "Hub not found. No associated hub record for the unit.",
    -5: "Internal Error.",
    -6: "Invalid load value.",
    -7: "Year missing.",
    -8: "Month missing or invalid.",
    -9: "Day missing or invalid.",
    -10: "Hour missing or invalid.",
    -11: "Invalid TTL Value.",
    -12: "User not authorised to perform operation.",
    -13: "Serial No not found.",
    -14: "Missing or bad parameter.",
    -15: "Invalid password.",
    -16: "New passwords don't match.",
    -17: "Invalid new password.",
    -18: "New password is same as old password.",
    -19: "User not registered.",
    -20: "Minute missing or invalid",
    -21: "Slot missing or invalid",
    -22: "Priority bad or missing",
    -23: "Command not appropriate for device",
    -24: "Check period bad or missing",
    -25: "Min Green Level bad or missing",
    -26: "Busy – Server is already sending a command to the device.",
    -27: "Relay not fitted."
}
