"""Support for Victron Energy devices."""

from collections import OrderedDict
import logging
import threading
from typing import Any

from packaging import version
import pymodbus
from pymodbus.client import ModbusTcpClient

from homeassistant.exceptions import HomeAssistantError

from .const import (
    INT16,
    INT32,
    STRING,
    UINT16,
    UINT32,
    register_info_dict,
    valid_unit_ids,
)

_LOGGER = logging.getLogger(__name__)


class VictronHub:
    """Victron Hub."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self._client = ModbusTcpClient(host=self.host, port=self.port)
        self._lock = threading.Lock()

    def is_still_connected(self) -> Any:
        """Check if the connection is still open."""
        return self._client.is_socket_open()

    def convert_string_from_register(
        self, segment: list[int], string_encoding: str = "ascii"
    ) -> Any:
        """Convert from registers to the appropriate data type."""
        if (
            version.parse("3.8.0")
            <= version.parse(pymodbus.__version__)
            <= version.parse("3.8.4")
        ):
            return self._client.convert_from_registers(
                segment, self._client.DATATYPE.STRING
            ).split("\x00")[0]
        return self._client.convert_from_registers(
            segment, self._client.DATATYPE.STRING, string_encoding=string_encoding
        ).split("\x00")[0]

    def convert_number_from_register(self, segment: list[int], data_type: Any) -> Any:
        """Convert from registers to the appropriate data type."""
        raw: Any | None = None
        if data_type == UINT16:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.UINT16
            )
        elif data_type == INT16:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.INT16
            )
        elif data_type == UINT32:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.UINT32
            )
        elif data_type == INT32:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.INT32
            )
        return raw

    def connect(self) -> Any:
        """Connect to the Modbus TCP server."""
        return self._client.connect()

    def disconnect(self) -> Any:
        """Disconnect from the Modbus TCP server."""
        if self._client.is_socket_open():
            return self._client.close()
        return None

    def write_register(self, unit: Any, address: int, value: int) -> Any:
        """Write a register."""
        slave = int(unit) if unit else 1
        return self._client.write_register(address=address, value=value, slave=slave)

    def read_holding_registers(self, unit: Any, address: int, count: int) -> Any:
        """Read holding registers."""
        slave = int(unit) if unit else 1
        return self._client.read_holding_registers(
            address=address, count=count, slave=slave
        )

    @staticmethod
    def calculate_register_count(register_info_dict_: OrderedDict | dict) -> Any:
        """Calculate the number of registers to read."""
        first_key = next(iter(register_info_dict_))
        last_key = next(reversed(register_info_dict_))
        end_correction = 1
        if register_info_dict_[last_key].data_type in (INT32, UINT32):
            end_correction = 2
        elif isinstance(register_info_dict_[last_key].data_type, STRING):
            end_correction = register_info_dict_[last_key].data_type.length

        return (
            register_info_dict_[last_key].register
            - register_info_dict_[first_key].register
        ) + end_correction

    @staticmethod
    def get_first_register_id(register_info_dict_: OrderedDict | dict) -> Any:
        """Return first register id."""
        first_register = next(iter(register_info_dict_))
        return register_info_dict_[first_register].register

    def determine_present_devices(self) -> Any:
        """Determine which devices are present."""
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
                            "result is error for unit: %s address: %s count: %s",
                            unit,
                            address,
                            count,
                        )
                    else:
                        working_registers.append(key)
                except HomeAssistantError as e:
                    _LOGGER.error(e)

            if len(working_registers) > 0:
                valid_devices[unit] = working_registers
            else:
                _LOGGER.debug("no registers found for unit: %s", unit)

        return valid_devices
