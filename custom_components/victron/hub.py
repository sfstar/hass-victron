"""Support for Victron Energy devices."""

from collections import OrderedDict
import logging
import threading

from pymodbus.client import ModbusTcpClient

from .const import (
    INT32,
    INT64,
    STRING,
    UINT32,
    UINT64,
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
        # Fail more quickly and only retry once before executing retry logic
        self._client = ModbusTcpClient(
            host=self.host, port=self.port, timeout=10, retries=1
        )
        self._lock = threading.Lock()

    def is_still_connected(self):
        """Check if the connection is still open."""
        return self._client.is_socket_open()

    def connect(self):
        """Connect to the Modbus TCP server."""
        return self._client.connect()

    def disconnect(self):
        """Disconnect from the Modbus TCP server."""
        if self._client.is_socket_open():
            return self._client.close()
        return None

    def write_register(self, unit, address, value):
        """Write a register."""
        try:
            slave = int(unit)
            if not unit:
                _LOGGER.error(
                    "Unit for this device (%s) isn't set correctly. Cannot write (%s) to register (%s). Ensure that the config was migrated to latest state by forcing a rescan",
                    unit,
                    value,
                    address,
                )
                return
            self._client.write_register(address=address, value=value, slave=slave)
        except BrokenPipeError:
            self.__handle_broken_pipe_error()

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        try:
            if not unit:
                return None

            slave = int(unit)
            return self._client.read_holding_registers(
                address=address, count=count, slave=slave
            )
        except BrokenPipeError:
            self.__handle_broken_pipe_error()
            return None
        except ValueError:
            _LOGGER.error(
                "Unit for this device (%s) isn't set correctly. Cannot read register (%s). Ensure that the config was migrated to latest state by forcing a rescan",
                unit,
                address,
            )

    def __handle_broken_pipe_error(self):
        _LOGGER.warning(
            "Connection to the remote gx device is broken, trying to reconnect"
        )
        if not self.is_still_connected():
            self.connect()
            _LOGGER.info("Connection to GX device re-established")

    def calculate_register_count(self, registerInfoDict: OrderedDict):
        """Calculate the number of registers to read."""
        first_key = next(iter(registerInfoDict))
        last_key = next(reversed(registerInfoDict))
        end_correction = 1
        if registerInfoDict[last_key].dataType in (INT32, UINT32):
            end_correction = 2
        elif registerInfoDict[last_key].dataType in (INT64, UINT64):
            end_correction = 4
        elif isinstance(registerInfoDict[last_key].dataType, STRING):
            end_correction = registerInfoDict[last_key].dataType.length

        return (
            registerInfoDict[last_key].register - registerInfoDict[first_key].register
        ) + end_correction

    def get_first_register_id(self, registerInfoDict: OrderedDict):
        """Return first register id."""
        first_register = next(iter(registerInfoDict))
        return registerInfoDict[first_register].register

    def determine_present_devices(self):
        """Determine which devices are present."""
        valid_devices = {}

        for unit in valid_unit_ids:
            working_registers = []
            for key, register_definition in register_info_dict.items():
                # VE.CAN device zero is present under unit 100. This seperates non system / settings entities into the seperate can device
                if unit == 100 and not key.startswith(("settings", "system")):
                    continue

                address = self.get_first_register_id(register_definition)
                count = self.calculate_register_count(register_definition)
                result = self.read_holding_registers(unit, address, count)
                if result is None:
                    _LOGGER.debug(
                        "result is error for unit: %s address: %s count: %s and result: %s",
                        unit,
                        address,
                        count,
                        result,
                    )
                else:
                    working_registers.append(key)

            if len(working_registers) > 0:
                valid_devices[unit] = working_registers
            else:
                _LOGGER.debug("no registers found for unit: %s", unit)

        return valid_devices
