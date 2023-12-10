"""This code contains dataclasses which enable the construction of REST API clients

RESTClient: The RESTClient data class represents the configuration for making API requests.
It includes information such as the API URL, authentication method, supported API endpoints, arguments, parameters,
and constants. """

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, date, time
from enum import Enum
from typing import get_origin

import dateutil.parser


@dataclass
class baseclass:
    """This dataclass provides the post_init code to handle the nested dataclasses
    and formatting of datetime entries"""

    def __post_init__(self):
        for entry in fields(self):
            if entry.type == str:
                pass
            elif entry.type == int:
                pass
            elif entry.type == float:
                pass
            elif entry.type == bool:
                pass
            elif issubclass(entry.type.__class__, range):
                pass
            # If the entry type is date then convert it from a string to a date object
            elif entry.type == date:
                if getattr(self, entry.name) is not None:
                    setattr(self, entry.name, dateutil.parser.parse(getattr(self, entry.name)).date())
            # If the entry type is time then convert it from a string to a time object
            elif entry.type == time:
                if getattr(self, entry.name) is not None:
                    setattr(self, entry.name, dateutil.parser.parse(getattr(self, entry.name)).time())
            # If the entry type is datetime then convert it from a string to a datetime object
            elif entry.type == datetime:
                if getattr(self, entry.name) is not None:
                    setattr(self, entry.name, dateutil.parser.parse(getattr(self, entry.name)))
            # If the entry type is a list
            elif get_origin(entry.type) == list:
                # If the type of the list entry is a dataclass then parse each entry of the list into the dataclass
                if is_dataclass(entry.type.__args__[0]):
                    for index, data in enumerate(getattr(self, entry.name)):
                        getattr(self, entry.name)[index] = entry.type.__args__[0](**(getattr(self, entry.name)[index]))
                # If the type of the list entry is an Enum then convert it to an Enum entry
                if issubclass(entry.type.__args__[0], Enum):
                    try:
                        getattr(self, entry.name)[index] = entry.type.__args__[0][data]
                    except KeyError:
                        setattr(self, entry.name, entry.type(getattr(self, entry.name)))
                    except TypeError:
                        pass
            # If the entry type is a dataclass and the entry is not null then parse the entry into the dataclass
            elif (is_dataclass(entry.type)) & (bool(getattr(self, entry.name)) is True):
                setattr(self, entry.name, entry.type(**(getattr(self, entry.name))))
            # If the entry type is an Enum then convert it to an Enum entry
            elif issubclass(entry.type, Enum):
                try:
                    setattr(self, entry.name, entry.type[getattr(self, entry.name)])
                except KeyError:
                    setattr(self, entry.name, entry.type(getattr(self, entry.name)))
                except TypeError:
                    pass
            # If the entry type is a dict and the entry is not null
            elif (get_origin(entry.type) == dict) & (bool(getattr(self, entry.name)) is True):
                # Create a new dict in case we have to change the index
                new_dict = {}
                for index, data in enumerate(getattr(self, entry.name)):
                    # if the dict value is a dataclass
                    if is_dataclass(entry.type.__args__[1]):
                        getattr(self, entry.name)[data] = entry.type.__args__[1](**(getattr(self, entry.name)[data]))
                    # if the dict index is an enum
                    if issubclass(entry.type.__args__[0], Enum):
                        # print(getattr(entry.type.__args__[0], data))
                        new_dict[getattr(entry.type.__args__[0], data)] = getattr(self, entry.name)[data]
                        # for index, data in enumerate(getattr(self, entry.name)):
                        #    getattr(self, entry.name)[index] = entry.type.__args__[0][entry.name]
                    else:
                        new_dict[data] = getattr(self, entry.name)[data]
                setattr(self, entry.name, new_dict)


@dataclass(frozen=True)
class Endpoint:
    """Dataclass describing API endpoints and the data they return."""
    response: object
    sample: str = None
    name: str = None
    endpoint: str = ""
    type: str = "get"
    auth: str = None
    arguments: list = field(default_factory=list)
    parms: list = field(default_factory=list)


@dataclass
class APIArguments:
    """Dataclass describing the set of arguments used by the API endpoints."""


@dataclass
class APIParameters:
    """Dataclass describing the set of parameters used by the API endpoints."""


@dataclass
class RESTClient:
    """This dataclass defines the set of information necessary to use a REST API.

    Attributes:
        url: The URL used for the REST API
        auth: The type of authorisation used
        apis: A list of the API Endpoints
        apiargs: A dataclass describing the set of arguments used by the endpoints
        apiparms: A dataclass describing the set of parameters used by the endpoints
        constants: A list of constants
    """
    url: str
    auth: str
    apilist: Enum
    arguments: APIArguments = None
    parameters: APIParameters = None
    constants: Enum = None
