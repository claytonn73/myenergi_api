"""Provide constants and dataclasses used by the myenergi API."""

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class WeekDay(Enum):
    """Human readable names for the days of the week returned in the history statistics."""
    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'


class MyEnergiEndpoint(Enum):
    """Supported endpoints for the Myenergi API and related constants."""
    DEVICES = "cgi-jstatus-*"
    HARVI = "cgi-jstatus-H"
    LIBBI = "cgi-jstatus-L"
    ZAPPI = "cgi-jstatus-Z"
    ZAPPI_MODE = "cgi-zappi-mode-Z"
    ZAPPI_MINGREEN = "cgi-set-min-green-Z"
    ZAPPI_BOOST_TIME = "cgi-boost-time-Z"
    ZAPPI_HISTORY_MINUTE = "cgi-jday-Z"
    ZAPPI_HISTORY_HOUR = "cgi-jdayhour-Z"
    EDDI = "cgi-jstatus-E"
    EDDI_PRIORITY = "cgi-set-heater-priority-E"
    EDDI_HISTORY_MINUTE = "cgi-jhour-E"
    EDDI_HISTORY_HOUR = "cgi-jday-E"
    EDDI_BOOST_TIME = "cgi-boost-time-E"
    EDDI_BOOST = "cgi-eddi-boost-E"
    DIRECTOR_URL = "https://director.myenergi.net"
    API_HEADERS = {'user-agent': 'python/0.0.1'}
    ASN_HEADER_FIELD = 'X_MYENERGI-asn'


class MyEnergiResponse(Enum):
    """A list of the return codes for the myenergi API and the human readable meaning."""
    Success = 0
    InvalidID = -1
    InvalidDSRCommandSequenceNumber = -2
    NoActionTakenCommandSequenceNumberSameAsLast = -3
    HubNotFoundNoAssociatedHubRecord = -4
    InternalError = -5
    InvalidLoadValue = -6
    YearMissing = -7
    MonthMissingOrInvalid = -8
    DayMissingOrInvalid = -9
    HourMissingOrInvalid = -10
    InvalidTTLValue = -11
    UserNotAuthorizedToPerformOperation = -12
    SerialNumberNotFound = -13
    MissingOrBadParameter = -14
    InvalidPassword = -15
    NewPasswordsDoNotMatch = -16
    InvalidNewPassword = -17
    NewPasswordSameAsOldPassword = -18
    UserNotRegistered = -19
    MinuteMissingOrInvalid = -20
    SlotMissingOrInvalid = -21
    PriorityBadOrMissing = -22
    CommandNotAppropriateForDevice = -23
    CheckPeriodBadOrMissing = -24
    MinGreenLevelBadOrMissing = -25
    BusyServerAlreadySendingCommandToDevice = -26
    RelayNotFitted = -27


class MyenergiType(Enum):
    """Supported Device Types and other Responses."""
    HARVI = "harvi"
    EDDI = "eddi"
    ZAPPI = "zappi"
    LIBBI = "libbi"
    URL = "asn"
    STATUS = "status"
    STATUS_TEXT = "statustext"
    FIRMWARE = "fwv"


class LoadTypes(Enum):
    """Text values for different load types in Zappi and Harvi API responses."""
    GENERATION = "Generation"
    GRID = "Grid"
    BATTERY = "AC Battery"
    SOLAR = "Solar"
    INTERNAL = "Internal Load"
    NONE = "None"


class History(Enum):
    """Types of history data that can be requested for the Zappi or Eddi."""
    MINUTE = "ZAPPI_HISTORY_MINUTE"
    HOUR = "ZAPPI_HISTORY_HOUR"


class EddiData(Enum):
    """Data returned for the Eddi."""
    DATE = "dat"
    TIME = "time"
    SERIAL_NUMBER = "sno"
    FREQUENCY = "frq"
    VOLTAGE = "vol"
    GENERATED_WATTS = "gen"
    GRID_WATTS = "grd"
    TIMESTAMP = "timestamp"
    CT1_NAME = "ectt1"
    CT2_NAME = "ectt2"
    CT1_WATTS = "ectp1"
    CT2_WATTS = "ectp2"
    STATUS = "sta"
    ACTIVE_HEATER = "hno"
    PHASE = "pha"
    HEATER_1 = "ht1"
    HEATER_2 = "ht2"
    TEMPERATURE_1 = "tp1"
    TEMPERATURE_2 = "tp2"
    PRIORITY = "pri"
    COMMAND_TIMER = "cmt"
    R1A = "r1a"
    R2A = "r2a"
    R2B = "r2b"
    REMAINING_BOOST = "rbt"
    HEATING_KWH = "che"


class EddiMode(Enum):
    """Numeric values of different Eddi modes."""
    STOPPED = 0
    NORMAL = 1


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
    TIMESTAMP = "timestamp"


class LibbiData(Enum):
    """Data returned for the Libbi."""
    batteryDischargingBoost = "batteryDischargingBoost"
    CMT = "cmt"
    DATE = "dat"
    DIVERTED_WATTS = "div"
    DST = "dst"
    CT1_PHASE = "ect1p"
    CT2_PHASE = "ect2p"
    CT3_PHASE = "ect3p"
    CT1_WATTS = "ectp1"
    CT2_WATTS = "ectp2"
    CT3_WATTS = "ectp3"
    CT4_WATTS = "ectp4"
    CT5_WATTS = "ectp5"
    CT1_NAME = "ectt1"
    CT2_NAME = "ectt2"
    CT3_NAME = "ectt3"
    CT4_NAME = "ectt4"
    CT5_NAME = "ectt5"
    CT6_NAME = "ectt6"
    FREQUENCY = "frq"
    FIRMWARE = "fwv"
    g100LockoutState = "g100LockoutState"
    GRID_WATTTS = "grd"
    ISP = "isp"
    MODE = "lmo"
    MBC = "mbc"
    MIC = "mic"
    newAppAvailable = "newAppAvailable"
    newBootloaderAvailable = "newBootloaderAvailable"
    PHASE = "pha"
    PRIORITY = "pri"
    pvDirectlyConnected = "pvDirectlyConnected"
    SERIAL_NUMBER = "sno"
    SOC = "soc"
    STATUS = "sta"
    TIME = "tim"
    TIMEZONE = "tz"
    VOLTAGE = "vol"
    TIMESTAMP = "timestamp"


class ZappiData(Enum):
    """Data returned for the Zappi."""
    DATE = "dat"
    TIME = "tim"
    DAYLIGHT_SAVINGS = "dst"
    SERIAL_NUMBER = "sno"
    FREQUENCY = "frq"
    VOLTAGE = "vol"
    CHARGE_STATUS = "pst"
    MODE = "zmo"
    STATUS = "sta"
    EV_STATUS = "zsh"
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
    CT5_WATTS = "ectp5"
    CT6_WATTS = "ectp6"
    HISTORY = "history"
    BOOST_TIMES = "boost_times"
    TIMESTAMP = "timestamp"


class ZappiModeParm(Enum):
    """API paramemters to set different Zappi modes."""

    FAST = "-1-0-0-0000"
    ECO = "-2-0-0-0000"
    ECO_PLUS = "-3-0-0-0000"
    STOP = "-4-0-0-0000"


class ZappiMode(Enum):
    """Numeric values of different Zappi modes."""
    FAST = 1
    ECO = 2
    ECO_PLUS = 3
    STOP = 4


class ZappiState(Enum):
    """A list of the Zappi Status (sta) values returned and their human readable meaning."""
    Starting = 0
    Paused = 1
    Demand_Side_Response = 2
    Charging = 3
    Boosting = 4
    Charge_Complete = 5


class ZappiStatus(Enum):
    """A list of the Zappi Status (sta) values returned and their human readable meaning."""
    A = "EV Disconnected"
    B1 = "EV Connected"
    B2 = "Waiting for EV"
    C1 = "EV Ready to Charge"
    C2 = "Charging"
    F = "Fault"


class ZappiStateDisplay(Enum):
    """A translation of the Zappi state and status combination into what is shown on the panel."""
    A1 = "EV Disconnected"
    A2 = "EV Disconnected"
    A3 = "EV Disconnected"
    A4 = "EV Disconnected"
    A5 = "EV Disconnected"
    B11 = "Waiting for surplus power"
    B12 = "Waiting for surplus power"
    B14 = "Waiting for EV"
    B15 = "Charge Complete"
    B21 = "Charge Delayed"
    B22 = "Charge Delayed"
    B24 = "Charge Delayed"
    B25 = "Charge Complete"
    C11 = "Waiting for surplus power"
    C12 = "Waiting for surplus power"
    C14 = "Boosting"
    C15 = "Charge Complete"
    C21 = "Charging"
    C22 = "Charging"
    C23 = "Charging"
    C24 = "Boosting"
    F1 = "Fault/Restart"
    F2 = "Fault/Restart"
    F3 = "Fault/Restart"
    F4 = "Fault/Restart"
    F5 = "Fault/Restart"


class ZappiEVStatus(Enum):
    """A list of the Zappi EV Status (zsh) values returned and their human readable meaning."""
    EV_STARTUP = 0
    EV_DISC = 1
    EV_JUST_DISCONNECTED = 2
    EV_CONNECTED_START = 3
    EV_CONNECTED = 4
    EVSE_SURPLUS_AVAILABLE = 5
    EVSE_LOCKED = 6
    EVSE_WAIT_FOR_TEMP = 7
    EVSE_WAITING_FOR_EV = 8
    EV_CHARGE_DELAYED = 9
    EV_CHARGE_COMPLETE = 10
    EVSE_RCD_CHECK = 11
    EVSE_CHARGING = 12
    EVSE_IMPORTING = 13
    EV_CHARGE_STOPPING = 14
    EV_READY_LEGACY_START = 15
    EV_READY_LEGACY = 16
    EVSE_WAIT_FOR_LIMIT = 17
    EV_VENT = 18
    EVSE_RESTARTING = 19
    EVSE_PHASE_SWITCHING_RESTART = 20
    EV_WRONG_CABLE = 21
    EVSE_BAD_PILOT = 22
    EVSE_FAULT_LOCK = 23
    EVSE_FAULT_OUTPUT = 24
    EVSE_FAULT_PE = 25
    EVSE_FAULT_COMS = 26
    EVSE_SELFTEST_FAILED = 27
    EVSE_FAULT_CONTACTOR = 28
    EVSE_FAULT_RCD_TRIP = 29
    EVSE_FAULT_OVERLOAD = 30
    EVSE_FAULT_VOLTAGE_RANGE = 31
    EVSE_FAULT_VOLTAGE_MISMATCH = 32
    EVSE_WRONG_PHASE_ROTATION = 33
    CHARGE_BLOCKED = 50
    EV_PRECON = 51
    EVSE_PHSW_DELAY = 52
    EVSE_CHARGE_STOPPED = 53
    EVSE_RANDOM_DELAY_WAIT = 54
    EVSE_RANDOM_DELAY_RAMP_DOWN = 55
    EVSE_RANDOM_DELAY_RAMP_UP = 56


class ZappiBoost(Enum):
    """API paramemters to control boosting of the Zappi."""
    START = "-0-10-"
    SMART = "-0-11-"
    STOP = "-0-2-0-0000"


class BoostTime(Enum):
    """Human readable names for the Zappi and Eddi boost data response."""
    SLOT = "slt"
    START_HOUR = "bsh"
    START_MINUTE = "bsm"
    END_HOUR = "bdh"
    END_MINUTE = "bdm"
    BOOST_DAYS = "bdd"


class ZappiStats(Enum):
    """Human readable names for the Zappi History Statistics."""
    GRID_IMPORTED = 'imp'
    GRID_EXPORTED = 'exp'
    SOLAR_GENERATED = 'gen'
    SOLAR_USED = 'gep'
    ZAPPI_DIVERTED = 'h1d'
    ZAPPI_IMPORTED = 'h1b'
    HOME_SOLAR = 'hos'
    HOME_GRID = 'hog'


@dataclass
class minute_data:
    """_This dataclass describes the history data by minute provided by the Zappi"""
    dow: WeekDay
    dom: range(1, 31)
    mon: range(1, 12)
    yr: range(1000, 9999)
    hr: range(23) = 0
    hog: int = 0
    hos: int = 0
    imp: int = 0
    exp: int = 0
    gep: int = 0
    gen: int = 0
    h1d: int = 0
    h1b: int = 0
    min: range(59) = 0
    v1: int = 0
    frq: int = 0
    pect1: int = 0
    pect2: int = 0
    nect1: int = 0
    nect2: int = 0
    pect3: int = 0
    nect3: int = 0
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.strptime(str(self.dom) + ":" + str(self.mon) + ":" + str(self.yr) + ":" +
                                           str(self.hr) + ":" + str(self.min), "%d:%m:%Y:%H:%M")
        self.v1 = round(self.v1/10, 1)
        self.frq = round(self.frq/100, 1)
        self.hog = self.imp - self.gen - self.h1b
        self.hos = self.gep - self.exp - self.h1d
        for stat in ZappiStats:
            setattr(self, stat, round(getattr(self, stat) / 60 / 1000, 3))


@dataclass
class minute_history:
    """_This dataclass describes the overall structure for minute level history data."""
    serial: int
    history_data: list[minute_data] = field(default_factory=list)

    def __post_init__(self):
        for index, entry in enumerate(self.history_data):
            if isinstance(entry, dict):
                self.history_data[index] = minute_data(**self.history_data[index])


@dataclass
class hourly_data:
    """_This dataclass describes the hourly history data provided by the Zappi"""
    dow: WeekDay
    dom: range(1, 31)
    mon: range(1, 12)
    yr: range(1000, 9999)
    hog: int = 0
    hos: int = 0
    h1d: int = 0
    h1b: int = 0
    imp: int = 0
    exp: int = 0
    gep: int = 0
    gen: int = 0
    hr: range(23) = 0
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.strptime(str(self.dom) + ":" + str(self.mon) + ":" +
                                           str(self.yr) + ":" + str(self.hr) + ":0", "%d:%m:%Y:%H:%M")
        self.hog = self.imp - self.gen - self.h1b
        self.hos = self.gep - self.exp - self.h1d
        for stat in ZappiStats:
            setattr(self, stat.value, round(getattr(self, stat.value) / 3600 / 1000, 2))


@dataclass
class hourly_history:
    """_This dataclass describes the overall structure for hourly history data."""
    serial: int
    history_data: list[hourly_data] = field(default_factory=list)

    def __post_init__(self):
        for index, entry in enumerate(self.history_data):
            if isinstance(entry, dict):
                self.history_data[index] = hourly_data(**self.history_data[index])


@dataclass
class daily_data:
    """_This dataclass describes the daily history data entry created from the Zappi hourly history"""
    timestamp: datetime
    hog: float = 0
    hos: float = 0
    h1d: float = 0
    h1b: float = 0
    imp: float = 0
    exp: float = 0
    gep: float = 0
    gen: float = 0


@dataclass
class daily_history:
    """_This dataclass describes the overall structure for daily history data."""
    serial: int
    history_data: list[daily_data] = field(default_factory=list)


@dataclass
class boosttime:
    """_This dataclass describes the data for a Zappi boost time."""
    slt: int
    bsh: int
    bsm: int
    bdh: int
    bdm: int
    bdd: str


@dataclass
class boosttimes:
    """_This dataclass describes the data returned for a query of Zappi boost times."""
    boost_times: list[boosttime] = field(default_factory=list)

    def __post_init__(self):
        for index, entry in enumerate(self.boost_times):
            if isinstance(entry, dict):
                self.boost_times[index] = boosttime(**self.boost_times[index])
        # Remove boost times which are not valid
        self.boost_times = [boost for boost in self.boost_times if boost.bdd != "00000000"]


@dataclass
class eddi:
    """_This dataclass describes the data returned for a Eddi."""
    dat: date
    tim: time
    ectp1: int
    ectp2: int
    ectt1: LoadTypes
    ectt2: LoadTypes
    frq: float
    gen: int
    grd: int
    hno: int
    pha: int
    sno: int
    sta: int
    vol: float
    ht1: str
    ht2: str
    tp1: int
    tp2: int
    pri: int
    cmt: int
    r1a: int
    r2a: int
    r2b: int
    che: int
    timestamp: datetime = field(init=False)
    boost_times: boosttimes = None

    def __post_init__(self):
        self.timestamp = datetime.strptime(str(self.dat + self.tim), "%d-%m-%Y%H:%M:%S")


@dataclass
class libbi:
    """_This dataclass describes the data returned for a Libbi."""
    dat: date
    tim: time
    batteryDischargingBoost: bool
    cmt: int
    div: int
    dst: int
    ect1p: int
    ect2p: int
    ect3p: int
    ectp1: int
    ectp2: int
    ectp3: int
    ectp4: int
    ectp5: int
    ectt1: LoadTypes
    ectt2: LoadTypes
    ectt3: LoadTypes
    ectt4: LoadTypes
    ectt5: LoadTypes
    ectt6: LoadTypes
    frq: float
    fwv: str
    g100LockoutState: str
    grd: int
    isp: bool
    lmo: str
    mbc: int
    mic: int
    newAppAvailable: bool
    newBootloaderAvailable: bool
    pha: int
    pri: int
    pvDirectlyConnected: bool
    sno: int
    soc: int
    sta: int
    tz: int
    vol: int
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.strptime(str(self.dat + self.tim), "%d-%m-%Y%H:%M:%S")
        if self.ectt1 == "None":
            self.ectt1 = None
        if self.ectt2 == "None":
            self.ectt2 = None
        if self.ectt3 == "None":
            self.ectt3 = None
        if self.ectt4 == "None":
            self.ectt4 = None
        if self.ectt5 == "None":
            self.ectt5 = None
        if self.ectt6 == "None":
            self.ectt6 = None


@dataclass
class harvi:
    """_This dataclass describes the data returned for a Harvi."""
    dat: date
    tim: time
    sno: int
    fwv: str
    ectt1: LoadTypes
    ectt2: LoadTypes
    ectt3: LoadTypes
    ectp1: int
    ectp2: int
    ectp3: int
    ect1p: int
    ect2p: int
    ect3p: int
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        if self.ectt1 == "None":
            self.ectt1 = None
        if self.ectt2 == "None":
            self.ectt2 = None
        if self.ectt3 == "None":
            self.ectt3 = None
        self.timestamp = datetime.strptime(str(self.dat + self.tim), "%d-%m-%Y%H:%M:%S")


@dataclass
class zappi:
    """_This dataclass describes the data returned for a Zappi."""
    bsm: int
    bss: int
    bst: int
    cmt: int
    dat: date
    div: int
    dst: range(1)
    ectp1: int
    ectp2: int
    ectp3: int
    ectt1: LoadTypes
    ectt2: LoadTypes
    ectt3: LoadTypes
    ectt4: LoadTypes
    ectt5: LoadTypes
    ectt6: LoadTypes
    frq: float
    fwv: str
    lck: int
    mgl: int
    pha: int
    pri: int
    pst: ZappiStatus._member_names_
    pwm: int
    sbh: range(23)
    sbk: int
    sno: int
    sta: int
    tz: int
    tim: time
    vol: float
    zmo: ZappiMode
    zs: int
    zsh: ZappiEVStatus._member_names_
    newAppAvailable: bool
    newBootloaderAvailable: bool
    beingTamperedWith: bool
    batteryDischargeEnabled: bool
    g100LockoutState: str
    rrac: int = 0
    che: int = 0
    rac: int = 0
    grd: int = 0
    zsl: int = 0
    gen: int = 0
    ectp4: int = 0
    ectp5: int = 0
    ectp6: int = 0
    rdc: int = None
    sbm: range(60) = None
    tbh: range(23) = None
    tbk: int = None
    tbm: range(60) = None
    timestamp: datetime = field(init=False)
    boost_times: boosttimes = None

    def __post_init__(self):
        if self.ectt1 == "None":
            self.ectt1 = None
        if self.ectt2 == "None":
            self.ectt2 = None
        if self.ectt3 == "None":
            self.ectt3 = None
        if self.ectt4 == "None":
            self.ectt4 = None
        if self.ectt5 == "None":
            self.ectt5 = None
        if self.ectt6 == "None":
            self.ectt6 = None
        self.timestamp = datetime.strptime(str(self.dat + self.tim), "%d-%m-%Y%H:%M:%S")
        # Voltage is supplied as an integer in decivolts so need to divide by 10
        self.vol = round(self.vol/10, 1)


@dataclass
class devices:
    """_This dataclass describes the data returned for the initial API query."""
    asn: str = ""
    fwv: str = ""
    zappi: dict[str, zappi] = field(default_factory=dict)
    harvi: dict[str, harvi] = field(default_factory=dict)
    eddi: dict[str, eddi] = field(default_factory=dict)
    libbi: dict[str, libbi] = field(default_factory=dict)
