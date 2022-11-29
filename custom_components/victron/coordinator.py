from __future__ import annotations

import logging

from .hub import VictronHub # TODO

from collections import OrderedDict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.register_read_message import ReadHoldingRegistersResponse

from datetime import timedelta

from .const import DOMAIN, UINT16, UINT32, INT16, INT32, STRING, RegisterInfo, register_info_dict

import math

_LOGGER = logging.getLogger(__name__)

class victronEnergyDeviceUpdateCoordinator(DataUpdateCoordinator):
    """Gather data for the energy device."""

    api: VictronHub
#todo compile dict of unit id and device type
    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: str,
        decodeInfo: OrderedDict,
        interval: int,
        ac_voltage: int,
        ac_current: int,
        dc_voltage: int,
        dc_current: int



    ) -> None:
        """Initialize Update Coordinator."""

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval))
        self.api = VictronHub(host, port)
        self.api.connect()
        self.decodeInfo = decodeInfo
        self.interval = interval
        self.ac_voltage = ac_voltage
        self.ac_current = ac_current
        self.dc_voltage = dc_voltage
        self.dc_current = dc_current

    # async def force_update_data(self) -> None:
    #     data = await self._async_update_data()
    #     self.async_set_updated_data(data)


    async def _async_update_data(self) -> dict:
        """Fetch all device and sensor data from api."""
        data = ""
        """Get the latest data from victron"""
        self.logger.debug("Fetching victron data")
        self.logger.debug(self.decodeInfo)
        
        register_list_names = []
        parsed_data = OrderedDict()

        for unit, registerInfo in self.decodeInfo.items():
            for name in registerInfo:
                data = await self.fetch_registers(unit, register_info_dict[name])
                #TODO safety check if result is actual data if not unavailable
                if data.isError():
                    #raise error
                    _LOGGER.error("no valid data returned for entities")
                else:
                    parsed_data = OrderedDict(list(parsed_data.items()) + list(self.parse_register_data(data, register_info_dict[name], unit).items()))

        return {
            "register_set": self.decodeInfo,
            "data": parsed_data
        }

    def parse_register_data(self, buffer: ReadHoldingRegistersResponse, registerInfo: OrderedDict(str, RegisterInfo), unit: int) -> dict:
        decoder = BinaryPayloadDecoder.fromRegisters(
        buffer.registers, byteorder=Endian.Big
        )
        decoded_data  = OrderedDict()
        for key,value in registerInfo.items():
            full_key = str(unit) + "." + key
            if value.dataType == UINT16:
                decoded_data[full_key] = self.decode_scaling(decoder.decode_16bit_uint(), value.scale, value.unit)
            elif value.dataType == INT16:
                decoded_data[full_key] = self.decode_scaling(decoder.decode_16bit_int(), value.scale, value.unit)
            elif value.dataType == UINT32:
                decoded_data[full_key] = self.decode_scaling(decoder.decode_32bit_uint(), value.scale, value.unit)
            elif value.dataType == INT32:
                decoded_data[full_key] = self.decode_scaling(decoder.decode_32bit_uint(), value.scale, value.unit)
            elif isinstance(value.dataType, STRING):
                decoded_data[full_key] = decoder.decode_string(value.dataType.readLength).split(b'\x00')[0] #TODO Accomodate for individual character length
            else:
                #TODO raise error for not supported datatype
                raise Exception("unknown datatype not supported")
        return decoded_data

    def decode_scaling(self, number, scale, unit):
        if scale == 0:
            return number
        else:
            if unit == "" and scale == 1:
                return round(number)
            else:
                return number / scale

    def encode_scaling(self, value, unit, scale):
        if scale == 0:
            return value
        else:
            if unit == "" and scale == 1:
                return round(value)
            else:
                return value * scale

    def get_data(self):
        return self.data

    async def async_update_local_entry(self, key, value):
        data = self.data
        data["data"][key] = value
        self.async_set_updated_data(data)


    def processed_data(self):
        return self.data

    async def fetch_registers(self, unit, registerData):
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_update, unit, registerData
            )

            return resp

        except:
            raise UpdateFailed("Fetching registers failed")

    def write_register(self, unit, address, value):
        # try:

            resp = self.api_write(unit, address, value)
        # except:
            # TODO raise specific write error
            # _LOGGER.error("failed to write to option")


    def api_write(self, unit, address, value):
        #recycle connection
        return self.api.write_register(unit=unit, address=address, value=value)
#        return self.api.write

    def api_update(self, unit, registerInfo):
        #recycle connection
        return self.api.read_holding_registers(
            unit=unit, address=self.api.get_first_register_id(registerInfo), count=self.api.calculate_register_count(registerInfo)
        )

        # Update all properties
        #TODO query the registers for a given device and return the parsed data
        # try:
        #     data: DeviceResponseEntry = {
        #         "device": await self.api.device(),
        #         "data": await self.api.data(),
        #         "state": await self.api.state(),
        #     }
        # except:
        #     lol = ""



        # except RequestError as ex:
        #     raise UpdateFailed("Device did not respond as expected") from ex

        return data

class DataEntry():

    def __init__(self, unit, value) -> None:
        self.unit = unit
        self.value = value