"""Config flow for victron integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol



from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from homeassistant.core import callback

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_INTERVAL, RegisterInfo, SCAN_REGISTERS
from .hub import VictronHub

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Required(CONF_INTERVAL, default=30): int
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    _LOGGER.debug("host = "+ data[CONF_HOST])
    _LOGGER.debug("port = "+ str(data[CONF_PORT]))
    hub = VictronHub(data[CONF_HOST], data[CONF_PORT])
    
    
    try:
        hub.connect()
        _LOGGER.debug("connection was succesfull")
        discovered_devices = await scan_connected_devices(hub=hub) 
        _LOGGER.debug("successfully discovered devices")  
    except:
        _LOGGER.error("failed to connect to the victron device") 
    return {
            "title": "victron",
            "data": discovered_devices 
        }


async def scan_connected_devices(hub: VictronHub) -> list:
    #TODO check all known unit ids automatically
    return hub.determine_present_devices()
    #return


class VictronFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for victron."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> VictronOptionFlowHandler:
        """Get the options flow for this handler."""
        return VictronOptionFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        already_configured = False

        if user_input[CONF_INTERVAL] < 1:
            user_input[CONF_INTERVAL] = 1

        try:
            #not yet working
            await self.async_set_unique_id("victron")
            self._abort_if_unique_id_configured()
        except Exception as e:
            errors["base"] = "already_configured"
            already_configured = True

        if not already_configured:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            
            #data property can't be changed in options flow if user wants to refresh
            options = user_input
            options[SCAN_REGISTERS] = info["data"]
            return self.async_create_entry(title=info["title"], data = {}, options=options)
#            return self.async_create_entry(title=info["title"], data = { "registers": info["data"] }, options=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )



class parsedEntry():

    def __init__(self, decoderInfo: RegisterInfo, value):
        self.decoderInfo = decoderInfo
        self.value = value


class VictronOptionFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.area = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}
        CONF_RESCAN = "rescan"

        config = dict(self.config_entry.options)

        if user_input is not None:
            if user_input[CONF_INTERVAL] not in (None, ""):
                config[CONF_INTERVAL] = user_input[CONF_INTERVAL]

            try:
                if user_input[CONF_RESCAN]:
                    info = await validate_input(self.hass, self.config_entry.options)
                    config[SCAN_REGISTERS] = info["data"]
                    _LOGGER.debug(info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"


            return self.async_create_entry(title="", data = config)

        return self.async_show_form(
            step_id="init",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INTERVAL, default=self.config_entry.options[CONF_INTERVAL]
                    ): vol.All(vol.Coerce(int)),
                    vol.Optional(CONF_RESCAN, default=False): bool,
                },
            ),
        )



class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

# class VictronSensorBase(CoordinatorEntity, SensorEntity):
#     should_poll = False
#     _attr_has_entity_name = True

#     def __init__(self, platform, config_entry, coordinator):
#         """Pass coordinator to CoordinatorEntity."""
#         super().__init__(coordinator)
#         """Initialize the sensor."""
#         self._platform = platform
#         self._config_entry = config_entry

#     @property
#     def device_info(self):
#         return self._platform.device_info

#     @property
#     def config_entry_id(self):
#         return self._config_entry.entry_id

#     @property
#     def config_entry_name(self):
#         return self._config_entry.data["name"]

#     @property
#     def available(self) -> bool:
#         return self._platform.online

#     @callback
#     def _handle_coordinator_update(self) -> None:
#         self.async_write_ha_state()

