"""Config flow for victron integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol



from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from homeassistant.helpers.selector import (
    SelectSelectorConfig,
    SelectSelector,
    SelectOptionDict,
)


from homeassistant.core import callback

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_INTERVAL, RegisterInfo, SCAN_REGISTERS, CONF_ADVANCED_OPTIONS, CONF_DC_SYSTEM_VOLTAGE, CONF_AC_SYSTEM_VOLTAGE, CONF_DC_CURRENT_LIMIT, CONF_AC_CURRENT_LIMIT, DC_VOLTAGES, AC_VOLTAGES
from .hub import VictronHub

_LOGGER = logging.getLogger(__name__)

CONF_RESCAN = "rescan"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Required(CONF_INTERVAL, default=30): int,
        vol.Optional(CONF_ADVANCED_OPTIONS, default=False): bool,
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
    return hub.determine_present_devices()


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
        else:
            if user_input[CONF_ADVANCED_OPTIONS]:
                _LOGGER.debug("configuring advanced options")
                self.host = user_input[CONF_HOST]
                self.port = user_input[CONF_PORT]
                self.interval = user_input[CONF_INTERVAL]
                self.advanced_options = user_input[CONF_ADVANCED_OPTIONS]
                return await self.async_step_advanced()

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
            return self.async_create_entry(title=info["title"], data = { SCAN_REGISTERS: info["data"] }, options=options)
#            return self.async_create_entry(title=info["title"], data = { "registers": info["data"] }, options=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_advanced(self, user_input=None):
        """Handle write support and limit settings if requested."""
        errors = {}

        if user_input is not None:
            if self.host is not None:


                options = user_input
                options[CONF_HOST] = self.host
                options[CONF_PORT] = self.port
                options[CONF_INTERVAL] = self.interval
                options[CONF_ADVANCED_OPTIONS] = bool(self.advanced_options)
                options[CONF_AC_SYSTEM_VOLTAGE] = int(user_input[CONF_AC_SYSTEM_VOLTAGE])
                options[CONF_DC_SYSTEM_VOLTAGE] = int(user_input[CONF_DC_SYSTEM_VOLTAGE])

                try:
                    info = await validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                _LOGGER.debug("setting up extra entry")
                return self.async_create_entry(title=info["title"], data = { SCAN_REGISTERS: info["data"] }, options=options)

        return self.async_show_form(
            step_id="advanced",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_AC_SYSTEM_VOLTAGE, default=str(AC_VOLTAGES["US"])): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in AC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(CONF_AC_CURRENT_LIMIT, default=0): vol.All(vol.Coerce(int, "must be a number")),
                    vol.Required(CONF_DC_SYSTEM_VOLTAGE, default=str(DC_VOLTAGES["lifepo4_12v"])): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in DC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(CONF_DC_CURRENT_LIMIT, default= 0): vol.All(vol.Coerce(int, "must be a number"))
                }))


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

    async def async_step_advanced(self, user_input=None):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        user_input.pop(CONF_RESCAN, None)
        #combine dictionaries with priority given to user_input
        dict_priority = {1 : user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]} 
        return self.async_create_entry(title="", data = combined_config)


    async def async_step_init_read(self, user_input=None):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        #combine dictionaries with priority given to user_input
        if user_input[CONF_RESCAN]:
            info = await validate_input(self.hass, config)
            self.hass.config_entries.async_update_entry(self.config_entry,
                data = { SCAN_REGISTERS: info["data"] },
                title=""
            )

        user_input.pop(CONF_RESCAN, None)
        dict_priority = {1 : user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]} 

        if user_input[CONF_ADVANCED_OPTIONS]:
            self.hass.config_entries.async_update_entry(self.config_entry,
            options=combined_config, title="")
            _LOGGER.debug("returning step init because advanced options were selected")
            errors = {}
            #move to dedicated function (the write show form) to allow for re-use
            return self.init_write_form(errors)
        else:
            return self.async_create_entry(title="", data = combined_config)

    async def async_step_init_write(self, user_input=None):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        #remove temp options =
        if user_input[CONF_RESCAN]:
            info = await validate_input(self.hass, config)
            self.hass.config_entries.async_update_entry(self.config_entry,
                data = { SCAN_REGISTERS: info["data"] },
                title=""
            )

        user_input.pop(CONF_RESCAN, None)
        #combine dictionaries with priority given to user_input
        dict_priority = {1 : user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]} 

        if not user_input[CONF_ADVANCED_OPTIONS]:
            self.hass.config_entries.async_update_entry(self.config_entry,
            options=combined_config, title="")
            _LOGGER.debug("returning step init because advanced options were selected")
            errors = {}
            #move to dedicated function (the write show form) to allow for re-use
            return self.init_read_form(errors)

        return self.async_create_entry(title="", data = combined_config)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}


        config = dict(self.config_entry.options)

        if user_input is not None:

            if user_input[CONF_INTERVAL] not in (None, ""):
                config[CONF_INTERVAL] = user_input[CONF_INTERVAL]

            try:
                if user_input[CONF_RESCAN]:
                    info = await validate_input(self.hass, self.config_entry.options)
                    #config[SCAN_REGISTERS] = info["data"]
                    _LOGGER.debug(info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            
            if user_input[CONF_RESCAN]:
                self.hass.config_entries.async_update_entry(self.config_entry,
                    data = { SCAN_REGISTERS: info["data"] },
                    title=""
                )
            #return self.async_create_entry(title="", data={})

            return self.async_create_entry(title="", data = config)

        if config[CONF_ADVANCED_OPTIONS]:
            _LOGGER.debug("advanced options is set")

            return self.init_write_form(errors)
        else:
            if user_input is None:
                return self.init_read_form(errors)


    def init_read_form(self, errors: dict):
        return self.async_show_form(
            step_id="init_read",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INTERVAL, default=self.config_entry.options[CONF_INTERVAL]
                    ): vol.All(vol.Coerce(int)),
                    vol.Optional(CONF_RESCAN, default=False): bool,
                    vol.Optional(CONF_ADVANCED_OPTIONS, default=False): bool
                },
            ),
        )

    def init_write_form(self, errors: dict):
        config = dict(self.config_entry.options)
        system_ac_voltage_default = self.config_entry.options.get(CONF_AC_SYSTEM_VOLTAGE, AC_VOLTAGES["US"])
        system_dc_voltage_default = self.config_entry.options.get(CONF_DC_SYSTEM_VOLTAGE, DC_VOLTAGES["lifepo4_12v"])
        errors = {}
        return self.async_show_form(
                step_id="init_write",
                errors=errors,
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_INTERVAL, default=self.config_entry.options[CONF_INTERVAL]
                        ): vol.All(vol.Coerce(int)),
                        vol.Required(CONF_AC_SYSTEM_VOLTAGE, default=str(system_ac_voltage_default)): SelectSelector(
                            SelectSelectorConfig(
                                options=[
                                    SelectOptionDict(value=str(value), label=key)
                                    for key, value in AC_VOLTAGES.items()
                                ]
                            ),
                        ),
                        vol.Required(CONF_AC_CURRENT_LIMIT, default=config.get(CONF_AC_CURRENT_LIMIT, 0)): vol.All(vol.Coerce(int, "must be a number")),
                        vol.Required(CONF_DC_SYSTEM_VOLTAGE, default=str(system_dc_voltage_default)): SelectSelector(
                            SelectSelectorConfig(
                                options=[
                                    SelectOptionDict(value=str(value), label=key)
                                    for key, value in DC_VOLTAGES.items()
                                ]
                            ),
                        ),
                        vol.Required(CONF_DC_CURRENT_LIMIT, default=config.get(CONF_DC_CURRENT_LIMIT,1)): vol.All(vol.Coerce(int, "must be a number")),
                        vol.Optional(CONF_RESCAN, default=False): bool,
                        vol.Optional(CONF_ADVANCED_OPTIONS, default=True): bool
                    },
                ),
            )

    def get_dict_key(self, dict, val):
        for key, value in dict.items():
            if val == value:
                return key
 
        return "key doesn't exist"

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

