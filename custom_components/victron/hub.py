from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

import threading
from collections import OrderedDict
from .const import UINT32, INT32, STRING, register_info_dict, valid_unit_ids

import logging

_LOGGER = logging.getLogger(__name__)

class VictronHub:

    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self._client = ModbusTcpClient(host=self.host, port=self.port)
        self._lock = threading.Lock()

    def connect(self):
        return self._client.connect()

    def write_register(self, unit, address, value):
        with self._lock:
            kwargs = {"slave": int(unit)} if unit else {}
            return self._client.write_register(address, value, **kwargs)

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        with self._lock:
            kwargs = {"slave": int(unit)} if unit else {}
            return self._client.read_holding_registers(address, count, **kwargs)

    def calculate_register_count(self, registerInfoDict: OrderedDict):
        first_key = next(iter(registerInfoDict))
        last_key = next(reversed(registerInfoDict))
        end_correction = 1
        if registerInfoDict[last_key].dataType in (INT32, UINT32):
            end_correction = 2
        elif isinstance(registerInfoDict[last_key].dataType, STRING):
            end_correction = registerInfoDict[last_key].dataType.length


        return (registerInfoDict[last_key].register - registerInfoDict[first_key].register) + end_correction

    def get_first_register_id(self, registerInfoDict: OrderedDict):
        first_register = next(iter(registerInfoDict))
        return registerInfoDict[first_register].register

    def determine_present_devices(self):
        valid_devices = {}

        for unit in valid_unit_ids:
            working_registers = []
            for key, register_definition in register_info_dict.items():
                try:
                    address = self.get_first_register_id(register_definition)
                    count = self.calculate_register_count(register_definition)
                    result = self.read_holding_registers(unit, address, count)
                    if result.isError():
                        _LOGGER.debug("result is error for unit: " + str(unit) + " address: " + str(address) + " count: " + str(count))
                    else:
                        working_registers.append(key)
                except Exception  as e:  # pylint: disable=broad-except
                    _LOGGER.error(e)


            if len(working_registers) > 0:
                valid_devices[unit] = working_registers
            else:
                _LOGGER.debug("no registers found for unit: " + str(unit))

        return valid_devices
