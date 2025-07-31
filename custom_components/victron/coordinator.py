"""Define the Victron Energy Device Update Coordinator."""

from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta
import logging
from typing import Any

import pymodbus

if "3.7.0" <= pymodbus.__version__ <= "3.7.4":
    from pymodbus.pdu.register_read_message import (  # pylint: disable=no-name-in-module
        ReadHoldingRegistersResponse,
    )
else:
    from pymodbus.pdu.register_message import ReadHoldingRegistersResponse

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    INT16,
    INT32,
    STRING,
    UINT16,
    UINT32,
    RegisterInfo,
    register_info_dict,
)
from .hub import VictronHub

_LOGGER = logging.getLogger(__name__)


class VictronEnergyDeviceUpdateCoordinator(DataUpdateCoordinator):  # type: ignore[misc]
    """Gather data for the energy device."""

    api: VictronHub

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        decode_info: OrderedDict,
        interval: int,
    ) -> None:
        """Initialize Update Coordinator."""

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval)
        )
        self.api = VictronHub(host, port)
        self.api.connect()
        self.decode_info = decode_info
        self.interval = interval

    # async def force_update_data(self) -> None:
    #     data = await self._async_update_data()
    #     self.async_set_updated_data(data)

    async def _async_update_data(self) -> dict:
        """Fetch all device and sensor data from api."""
        self.data: dict | None
        # Get the latest data from victron
        self.logger.debug("Fetching victron data")
        self.logger.debug(self.decode_info)

        parsed_data: OrderedDict = OrderedDict()
        unavailable_entities = OrderedDict()

        if self.data is None:
            self.data = {"data": OrderedDict(), "availability": OrderedDict()}

        for unit, registerInfo in self.decode_info.items():
            for name in registerInfo:
                data = await self.fetch_registers(unit, register_info_dict[name])
                # TODO safety check if result is actual data if not unavailable
                if data.isError():
                    # raise error
                    # TODO change this to work with partial updates
                    for key in register_info_dict[name]:
                        full_key = str(unit) + "." + key
                        # self.data["data"][full_key] = None
                        unavailable_entities[full_key] = False

                    _LOGGER.warning(
                        "No valid data returned for entities of slave: %s (if the device continues to no longer update) check if the device was physically removed. Before opening an issue please force a rescan to attempt to resolve this issue",
                        unit,
                    )
                else:
                    parsed_data = OrderedDict(
                        list(parsed_data.items())
                        + list(
                            self.parse_register_data(
                                data, register_info_dict[name], unit
                            ).items()
                        )
                    )
                    for key in register_info_dict[name]:
                        full_key = str(unit) + "." + key
                        unavailable_entities[full_key] = True

        return {
            "register_set": self.decode_info,
            "data": parsed_data,
            "availability": unavailable_entities,
        }

    def parse_register_data(
        self,
        buffer: ReadHoldingRegistersResponse,
        register_info: OrderedDict[str, RegisterInfo] | dict,
        unit: int,
    ) -> dict:
        """Parse the register data using convert_from_registers."""
        decoded_data = OrderedDict()
        registers = buffer.registers
        offset = 0

        for key, value in register_info.items():
            full_key = f"{unit}.{key}"
            count = 0
            if value.data_type in (INT16, UINT16):
                count = 1
            elif value.data_type in (INT32, UINT32):
                count = 2
            elif isinstance(value.data_type, STRING):
                count = value.data_type.length
            segment = registers[offset : offset + count]

            if isinstance(value.data_type, STRING):
                raw = self.api.convert_string_from_register(segment)
                decoded_data[full_key] = raw
            else:
                raw = self.api.convert_number_from_register(segment, value.data_type)
                # _LOGGER.warning("trying to decode %s with value %s", key, raw)
                decoded_data[full_key] = self.decode_scaling(
                    raw, value.scale, value.unit
                )
            offset += count

        return decoded_data

    @staticmethod
    def decode_scaling(number: Any, scale: Any, unit: Any) -> Any:
        """Decode the scaling."""
        if unit == "" and scale == 1:
            return round(number)
        return number / scale

    @staticmethod
    def encode_scaling(value: Any, unit: Any, scale: Any) -> Any:
        """Encode the scaling."""
        if scale == 0:
            return value
        if unit == "" and scale == 1:
            return int(round(value))
        return int(value * scale)

    def get_data(self) -> Any:
        """Return the data."""
        return self.data

    async def async_update_local_entry(self, key: Any, value: Any) -> Any:
        """Update the local entry."""
        data = self.data
        if data:
            data["data"][key] = value
            self.async_set_updated_data(data)

            await self.async_request_refresh()

    def processed_data(self) -> dict[Any, Any]:
        """Return the processed data."""
        return self.data  # type:ignore[return-value]

    async def fetch_registers(self, unit: Any, register_data: Any) -> Any:
        """Fetch the registers."""
        try:
            # run api_update in async job
            return await self.hass.async_add_executor_job(
                self.api_update, unit, register_data
            )

        except HomeAssistantError as e:
            raise UpdateFailed("Fetching registers failed") from e

    def write_register(self, unit: Any, address: Any, value: Any) -> Any:
        """Write to the register."""
        # try:

        self.api_write(unit, address, value)

    # except HomeAssistantError as e:
    # TODO raise specific write error
    # _LOGGER.error("failed to write to option:", e

    def api_write(self, unit: Any, address: Any, value: Any) -> Any:
        """Write to the api."""
        # recycle connection
        return self.api.write_register(unit=unit, address=address, value=value)

    def api_update(self, unit: Any, register_info: Any) -> Any:
        """Update the api."""
        # recycle connection
        return self.api.read_holding_registers(
            unit=unit,
            address=self.api.get_first_register_id(register_info),
            count=self.api.calculate_register_count(register_info),
        )


class DecodeDataTypeUnsupported(Exception):
    """Exception for unsupported data type."""


class DataEntry:
    """Data entry class."""

    def __init__(self, unit: Any, value: Any) -> None:
        """Initialize the data entry."""
        self.unit = unit
        self.value = value
