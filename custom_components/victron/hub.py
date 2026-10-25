"""Support for Victron Energy devices."""

from collections import OrderedDict
import logging
import threading

from packaging import version
import pymodbus
from pymodbus.client import ModbusTcpClient

from homeassistant.exceptions import HomeAssistantError

from .const import (
    INT16,
    INT32,
    INT64,
    STRING,
    TextReadEntityType,
    UINT16,
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
        self._client = ModbusTcpClient(host=self.host, port=self.port)
        self._lock = threading.Lock()

    def is_still_connected(self):
        """Check if the connection is still open."""
        return self._client.is_socket_open()

    def convert_string_from_register(self, segment, string_encoding="ascii"):
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

    def convert_number_from_register(self, segment, dataType):
        """Convert from registers to the appropriate data type."""
        if dataType == UINT16:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.UINT16
            )
        elif dataType == INT16:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.INT16
            )
        elif dataType == UINT32:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.UINT32
            )
        elif dataType == INT32:
            raw = self._client.convert_from_registers(
                segment, data_type=self._client.DATATYPE.INT32
            )
        return raw

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
        slave = int(unit) if unit else 1
        return self._client.write_register(
            address=address, value=value, device_id=slave
        )

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        slave = int(unit) if unit else 1
        _LOGGER.debug("Reading unit %s address %s count %s", unit, address, count)
        return self._client.read_holding_registers(
            address=address, count=count, device_id=slave
        )

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

        _LOGGER.debug("Determining present devices")

        for unit in valid_unit_ids:
            working_registers = []
            for key, register_definition in register_info_dict.items():
                _LOGGER.debug("Checking unit %s for register set %s", unit, key)
                # Unit 0 and unit 100 map to the same GX system address. Keep
                # system/settings entities on unit 100 while allowing a real
                # VE.CAN device at unit 0 to own its device-specific entities.
                if (unit == 100 and not key.startswith(("settings", "system"))) or (
                    unit == 0 and key.startswith(("settings", "system"))
                ):
                    continue

                try:
                    status = self._probe_block_supported(unit, register_definition)
                except HomeAssistantError as e:
                    _LOGGER.error(e)
                    continue

                if status is True:
                    working_registers.append(key)
                elif status is False:
                    _LOGGER.debug(
                        "register set %s on unit %s returned undecodable text "
                        "values across all probe attempts; treating as not present",
                        key,
                        unit,
                    )
                else:
                    _LOGGER.debug(
                        "register set %s on unit %s did not respond on any "
                        "probe attempt; treating as not present",
                        key,
                        unit,
                    )

            if len(working_registers) > 0:
                valid_devices[unit] = working_registers
            else:
                _LOGGER.debug("no registers found for unit: %s", unit)

        return valid_devices

    def _probe_block_supported(
        self, unit, register_definition: OrderedDict, attempts: int = 3
    ):
        """Probe a register block multiple times. Tristate result.

        Returns ``True`` if at least one read returned valid (decodable) data,
        ``False`` if every successful read had undecodable TextReadEntityType
        values, and ``None`` if every attempt errored or raised. Multi-read
        consensus prevents a single transient bad value (e.g. a 0xFFFF sentinel
        emitted briefly during a device reset) from permanently marking a block
        as not-present, while still pruning blocks that consistently return
        garbage for registers the hardware does not actually populate.
        """
        address = self.get_first_register_id(register_definition)
        count = self.calculate_register_count(register_definition)
        saw_undecodable = False
        for _ in range(attempts):
            try:
                result = self.read_holding_registers(unit, address, count)
            except Exception:  # noqa: BLE001 — bounded retry; transient errors are expected
                continue
            if result.isError():
                continue
            if self._block_has_undecodable_text(
                register_definition, result, address
            ):
                saw_undecodable = True
                continue
            return True
        if saw_undecodable:
            return False
        return None

    def revalidate_register_set(self, stored: dict) -> dict:
        """Re-probe a previously stored register set and prune blocks no longer supported.

        Uses the same multi-read consensus probe as ``determine_present_devices``:
        a block is dropped only if every successful read returns undecodable
        TextReadEntityType values. Blocks that error on every attempt (e.g.
        device temporarily unreachable) are kept in place -- this revalidation
        runs at HA startup and a transient outage must not wipe a working
        configuration.

        Existing config entries can carry register blocks that were detected
        before ``determine_present_devices`` learned to validate
        TextReadEntityType contents; this lets ``async_setup_entry`` heal them
        at startup without requiring users to re-add the integration.
        """
        pruned: dict = {}
        for unit, blocks in stored.items():
            kept = []
            for key in blocks:
                register_definition = register_info_dict.get(key)
                if register_definition is None:
                    # Block no longer exists in the integration; drop it.
                    continue
                status = self._probe_block_supported(unit, register_definition)
                if status is False:
                    _LOGGER.info(
                        "Pruning register block %s on unit %s: text register "
                        "no longer decodes against its enum across all probe "
                        "attempts",
                        key,
                        unit,
                    )
                    continue
                # status is True (supported) or None (transient error) -- keep.
                kept.append(key)
            if kept:
                pruned[unit] = kept
        return pruned

    def _block_has_undecodable_text(
        self, register_definition: OrderedDict, result, first_address: int
    ) -> bool:
        """Return True if any TextReadEntityType register in the block decodes outside its enum.

        Some Victron devices return well-formed Modbus responses with garbage values
        for registers their hardware does not actually populate (e.g. battery_balancer_status
        on a BMS without a Battery Balancer).
        """
        for info in register_definition.values():
            if not isinstance(info.entityType, TextReadEntityType):
                continue
            offset = info.register - first_address
            if offset < 0 or offset >= len(result.registers):
                continue
            valid_values = {item.value for item in info.entityType.decodeEnum}
            if result.registers[offset] not in valid_values:
                return True
        return False
