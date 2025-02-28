"""Define the Victron Energy Device Update Coordinator."""

from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta
import logging

import pymodbus
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

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
    INT64,
    STRING,
    UINT16,
    UINT32,
    UINT64,
    RegisterInfo,
    register_info_dict,
)
from .hub import VictronHub

_LOGGER = logging.getLogger(__name__)


class victronEnergyDeviceUpdateCoordinator(DataUpdateCoordinator):
    """Gather data for the energy device."""

    api: VictronHub

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: str,
        decodeInfo: OrderedDict,
        interval: int,
    ) -> None:
        """Initialize Update Coordinator."""

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval)
        )
        self.api = VictronHub(host, port)
        self.api.connect()
        self.decodeInfo = decodeInfo
        self.interval = interval

    # async def force_update_data(self) -> None:
    #     data = await self._async_update_data()
    #     self.async_set_updated_data(data)

    async def _async_update_data(self) -> dict:
        """Fetch all device and sensor data from api."""
        data = ""
        """Get the latest data from victron"""
        self.logger.debug("Fetching victron data")
        self.logger.debug(self.decodeInfo)

        parsed_data = OrderedDict()
        available_entities = OrderedDict()

        if self.data is None:
            self.data = {"data": OrderedDict(), "availability": OrderedDict()}

        for unit, registerInfo in self.decodeInfo.items():
            for name in registerInfo:
                data = await self.fetch_registers(unit, register_info_dict[name])
                # TODO safety check if result is actual data if not unavailable
                if data.isError():
                    # raise error
                    # TODO change this to work with partial updates
                    for key in register_info_dict[name]:
                        full_key = str(unit) + "." + key
                        available_entities[full_key] = False

                    _LOGGER.warning(
                        "No valid data: %s returned for entities of slave: %s (if the device continues to no longer update) check if the device was physically removed. Before opening an issue please force a rescan to attempt to resolve this issue",
                        data,
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
                        available_entities[full_key] = True

        return {
            "register_set": self.decodeInfo,
            "data": parsed_data,
            "availability": available_entities,
        }

    def parse_register_data(
        self,
        buffer: ReadHoldingRegistersResponse,
        registerInfo: OrderedDict(str, RegisterInfo),
        unit: int,
    ) -> dict:
        """Parse the register data."""
        decoder = BinaryPayloadDecoder.fromRegisters(
            buffer.registers, byteorder=Endian.BIG
        )
        decoded_data = OrderedDict()
        for key, value in registerInfo.items():
            full_key = str(unit) + "." + key
            if value.dataType == UINT16:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_16bit_uint(), value.scale, value.unit
                )
            elif value.dataType == INT16:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_16bit_int(), value.scale, value.unit
                )
            elif value.dataType == UINT32:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_32bit_uint(), value.scale, value.unit
                )
            elif value.dataType == INT32:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_32bit_int(), value.scale, value.unit
                )
            elif value.dataType == UINT64:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_64bit_uint(), value.scale, value.unit
                )
            elif value.dataType == INT64:
                decoded_data[full_key] = self.decode_scaling(
                    decoder.decode_64bit_int(), value.scale, value.unit
                )
            elif isinstance(value.dataType, STRING):
                decoded_data[full_key] = (
                    decoder.decode_string(value.dataType.readLength)
                    .split(b"\x00")[0]
                    .decode()
                )
            else:
                raise DecodeDataTypeUnsupported(
                    f"Not supported dataType: {value.dataType}"
                )
        return decoded_data

    def decode_scaling(self, number, scale, unit):
        """Decode the scaling."""
        if unit == "" and scale == 1:
            return round(number)
        return number / scale

    def encode_scaling(self, value, unit, scale):
        """Encode the scaling."""
        if scale == 0:
            return value
        if unit == "" and scale == 1:
            return int(round(value))
        return int(value * scale)

    def get_data(self):
        """Return the data."""
        return self.data

    async def async_update_local_entry(self, key, value):
        """Update the local entry."""
        data = self.data
        data["data"][key] = value
        self.async_set_updated_data(data)

        await self.async_request_refresh()

    def processed_data(self):
        """Return the processed data."""
        return self.data

    async def fetch_registers(self, unit, registerData):
        """Fetch the registers."""
        try:
            # run api_update in async job
            return await self.hass.async_add_executor_job(
                self.api_update, unit, registerData
            )

        except HomeAssistantError as e:
            raise UpdateFailed("Fetching registers failed") from e

    def write_register(self, unit, address, value):
        """Write to the register."""
        self.api_write(unit, address, value)

    def api_write(self, unit, address, value):
        """Write to the api."""
        # recycle connection
        return self.api.write_register(unit=unit, address=address, value=value)

    def api_update(self, unit, registerInfo):
        """Update the api."""
        # recycle connection
        return self.api.read_holding_registers(
            unit=unit,
            address=self.api.get_first_register_id(registerInfo),
            count=self.api.calculate_register_count(registerInfo),
        )


class DecodeDataTypeUnsupported(Exception):
    """Exception for unsupported data type."""


class DataEntry:
    """Data entry class."""

    def __init__(self, unit, value) -> None:
        """Initialize the data entry."""
        self.unit = unit
        self.value = value
