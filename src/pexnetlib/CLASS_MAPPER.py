from typing import Type
from pexnetlib.base_connection import BaseConnection
from pexnetlib.async_base_connection import AsyncBaseConnection
from pexnetlib.vender.cisco_connection import CiscoConnection, CiscoConnectionAsync
from pexnetlib.vender.apresia_connection import ApresiaConnection, ApresiaConnectionAsync

CLASS_MAPPER_SYNC: dict[str, Type[BaseConnection]] = {
	"cisco_telnet": CiscoConnection,
	"apresia_telnet": ApresiaConnection
}

CLASS_MAPPER_ASYNC: dict[str, Type[AsyncBaseConnection]] = {
	"cisco_telnet": CiscoConnectionAsync,
	"apresia_telnet": ApresiaConnectionAsync
}