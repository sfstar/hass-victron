"""Define the Victron Energy Device Update Coordinator."""

from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta
import logging
from typing import Any, Generic, TypeVar

import pymodbus
from pymodbus.constants import Endian

# this import needs to be able to be completely removed if the preparation for 3.9.0 is done
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.pdu import ModbusPDU

if "3.7.0" <= pymodbus.__version__ <= "3.7.4":
    from pymodbus.pdu.register_read_message import ReadHoldingRegistersResponse
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

_DataT = TypeVar("_DataT", default=dict[str, Any])

_LOGGER = logging.getLogger(__name__)


class VictronEnergyDeviceUpdateCoordinator(DataUpdateCoordinator, Generic[_DataT]):  # type: ignore[misc]
    """Gather data for the energy device."""

    api: VictronHub

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: str,
        decode_info: OrderedDict,
        interval: int,
    ) -> None:
        """Initialize Update Coordinator."""

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval)
        )
        self.api = VictronHub(host, port)
        self.api.connect()
        self.decodeInfo = decode_info
        self.interval = interval

    # async def force_update_data(self) -> None:
    #     data = await self._async_update_data()
    #     self.async_set_updated_data(data)

    async def _async_update_data(self) -> dict:
        """Get the latest data from victron."""
        self.logger.debug("Fetching victron data")
        self.logger.debug(self.decodeInfo)

        parsed_data: dict = OrderedDict()
        unavailable_entities: dict = OrderedDict()

        if self.data is None:
            self.data: dict[str, _DataT] = {  # type: ignore[unreachable]
                "data": OrderedDict(),
                "availability": OrderedDict(),
            }

        for unit, registerInfo in self.decodeInfo.items():
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
            "register_set": self.decodeInfo,
            "data": parsed_data,
            "availability": unavailable_entities,
        }

    def parse_register_data(
        self,
        buffer: ReadHoldingRegistersResponse,
        register_info: dict[str, RegisterInfo],
        unit: int,
    ) -> dict:
        """Parse the register data."""
        decoder = BinaryPayloadDecoder.fromRegisters(
            buffer.registers, byteorder=Endian.BIG
        )
        decoded_data = OrderedDict()
        for key, value in register_info.items():
            full_key = str(unit) + "." + key
            if value.data_type == UINT16:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_16bit_uint(), value.scale, value.unit
                )
            elif value.data_type == INT16:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_16bit_int(), value.scale, value.unit
                )
            elif value.data_type == UINT32:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_32bit_uint(), value.scale, value.unit
                )
            elif value.data_type == INT32:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_32bit_int(), value.scale, value.unit
                )
            elif isinstance(value.data_type, STRING):
                decoded_data[full_key] = (
                    decoder.decode_string(value.data_type.read_length)
                    .split(b"\x00")[0]
                    .decode()
                )
            else:
                raise DecodedataTypeUnsupported(
                    f"Not supported data_type: {value.data_type}"
                )
        return decoded_data

    def decode_scaling(self, number: float, scale: float, unit: str | None) -> float:
        """Decode the scaling.

        :param number:
        :param scale:
        :param unit:
        :return:
        """
        if unit == "" and scale == 1:
            return round(number)
        return number / scale

    def encode_scaling(self, value: float, unit: str, scale: int | None) -> Any:
        """Encode the scaling.

        :param value:
        :param unit:
        :param scale:
        :return:
        """
        if scale == 0:
            return value
        if unit == "" and scale == 1:
            return int(round(value))
        if scale is not None:
            return int(value * scale)
        return None

    def get_data(self) -> dict[str, _DataT]:
        """Return the data."""
        return self.data

    async def async_update_local_entry(self, key: str, value: Any) -> Any:
        """Update the local entry.

        :param key:
        :param value:
        :return:
        """
        data = self.data
        data["data"][key] = value  # type:ignore[index]
        self.async_set_updated_data(data)

        await self.async_request_refresh()

    def processed_data(self) -> Any:
        """Return the processed data."""
        return self.data

    async def fetch_registers(
        self, unit: str, register_data: dict[str, RegisterInfo]
    ) -> Any:
        """Fetch the registers.

        :param unit:
        :param register_data:
        :return:
        """
        try:
            # run api_update in async job
            return await self.hass.async_add_executor_job(
                self.api_update, unit, register_data
            )

        except HomeAssistantError as e:
            raise UpdateFailed("Fetching registers failed") from e

    def write_register(
        self, unit: int | None, address: float | None, value: float
    ) -> None:
        """Write to the register.

        :param unit:
        :param address:
        :param value:
        :return:
        """
        # try:

        self.api_write(unit, address, value)

    # except HomeAssistantError as e:
    # TODO raise specific write error
    # _LOGGER.error("failed to write to option:", e

    def api_write(
        self, unit: int | None, address: float | None, value: float
    ) -> ModbusPDU:
        """Write to the api."""
        # recycle connection
        return self.api.write_register(unit=unit, address=address, value=value)

    def api_update(self, unit: int, register_info: dict[str, RegisterInfo]) -> Any:
        """Update the api.

        :param unit:
        :param register_info:
        :return:
        """
        # recycle connection
        return self.api.read_holding_registers(
            unit=unit,
            address=self.api.get_first_register_id(register_info),
            count=self.api.calculate_register_count(register_info),
        )


class DecodedataTypeUnsupported(Exception):
    """Exception for unsupported data type."""


class DataEntry:
    """Data entry class."""

    def __init__(self, unit: int, value: int) -> None:
        """Initialize the data entry.

        :param unit:
        :param value:
        """
        self.unit = unit
        self.value = value
