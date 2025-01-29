from collections import OrderedDict
import logging
import threading

from pymodbus.client import ModbusTcpClient

from homeassistant.exceptions import HomeAssistantError

from .const import INT32, STRING, UINT32, register_info_dict, valid_unit_ids

_LOGGER = logging.getLogger(__name__)


class VictronHub:
    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self._client = ModbusTcpClient(host=self.host, port=self.port)
        self._lock = threading.Lock()

    def is_still_connected(self):
        return self._client.is_socket_open()

    def connect(self):
        return self._client.connect()

    def disconnect(self):
        if self._client.is_socket_open():
            return self._client.close()
        return None

    def write_register(self, unit, address, value):
        slave = int(unit) if unit else 1
        return self._client.write_register(address=address, value=value, slave=slave)

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        slave = int(unit) if unit else 1
        return self._client.read_holding_registers(
            address=address, count=count, slave=slave
        )

    def calculate_register_count(self, registerInfoDict: OrderedDict):
        first_key = next(iter(registerInfoDict))
        last_key = next(reversed(registerInfoDict))
        end_correction = 1
        if registerInfoDict[last_key].dataType in (INT32, UINT32):
            end_correction = 2
        elif isinstance(registerInfoDict[last_key].dataType, STRING):
            end_correction = registerInfoDict[last_key].dataType.length

        return (
            registerInfoDict[last_key].register - registerInfoDict[first_key].register
        ) + end_correction

    def get_first_register_id(self, registerInfoDict: OrderedDict):
        first_register = next(iter(registerInfoDict))
        return registerInfoDict[first_register].register

    def determine_present_devices(self):
        valid_devices = {}

        for unit in valid_unit_ids:
            working_registers = []
            for key, register_definition in register_info_dict.items():
                # VE.CAN device zero is present under unit 100. This seperates non system / settings entities into the seperate can device
                if unit == 100 and not key.startswith(("settings", "system")):
                    continue

                try:
                    address = self.get_first_register_id(register_definition)
                    count = self.calculate_register_count(register_definition)
                    result = self.read_holding_registers(unit, address, count)
                    if result.isError():
                        _LOGGER.debug(
                            "result is error for unit: "
                            + str(unit)
                            + " address: "
                            + str(address)
                            + " count: "
                            + str(count)
                        )
                    else:
                        working_registers.append(key)
                except HomeAssistantError as e:
                    _LOGGER.error(e)

            if len(working_registers) > 0:
                valid_devices[unit] = working_registers
            else:
                _LOGGER.debug("no registers found for unit: " + str(unit))

        return valid_devices
