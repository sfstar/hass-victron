"""Config flow for victron integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    AC_VOLTAGES,
    CONF_AC_CURRENT_LIMIT,
    CONF_AC_SYSTEM_VOLTAGE,
    CONF_ADVANCED_OPTIONS,
    CONF_DC_CURRENT_LIMIT,
    CONF_DC_SYSTEM_VOLTAGE,
    CONF_HOST,
    CONF_INTERVAL,
    CONF_NUMBER_OF_PHASES,
    CONF_PORT,
    CONF_USE_SLIDERS,
    DC_VOLTAGES,
    DOMAIN,
    PHASE_CONFIGURATIONS,
    SCAN_REGISTERS,
    RegisterInfo,
)
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

    _LOGGER.debug("host = %s", data[CONF_HOST])
    _LOGGER.debug("port = %s", data[CONF_PORT])
    hub = VictronHub(data[CONF_HOST], data[CONF_PORT])

    try:
        hub.connect()
        _LOGGER.debug("connection was succesfull")
        discovered_devices = await scan_connected_devices(hub=hub)
        _LOGGER.debug("successfully discovered devices")
    except HomeAssistantError:
        _LOGGER.error("Failed to connect to the victron device:")
    return {"title": DOMAIN, "data": discovered_devices}


async def scan_connected_devices(hub: VictronHub) -> list:
    """Scan for connected devices."""
    return hub.determine_present_devices()


class VictronFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for victron."""

    _LOGGER = logging.getLogger(__name__)
    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.advanced_options = None
        self.interval = None
        self.port = None
        self.host = None

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
        if user_input[CONF_ADVANCED_OPTIONS]:
            _LOGGER.debug("configuring advanced options")
            self.host = user_input[CONF_HOST]
            self.port = user_input[CONF_PORT]
            self.interval = user_input[CONF_INTERVAL]
            self.advanced_options = user_input[CONF_ADVANCED_OPTIONS]
            return await self.async_step_advanced()

        errors = {}
        already_configured = False

        user_input[CONF_INTERVAL] = max(user_input[CONF_INTERVAL], 1)

        try:
            # not yet working
            await self.async_set_unique_id("victron")
            self._abort_if_unique_id_configured()
        except HomeAssistantError as e:
            errors["base"] = f"already_configured: {e!s}"
            already_configured = True

        if not already_configured:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except HomeAssistantError:
                _LOGGER.exception("Unexpected exception:")
                errors["base"] = "unknown"

            # data property can't be changed in options flow if user wants to refresh
            options = user_input
            return self.async_create_entry(
                title=info["title"],
                data={SCAN_REGISTERS: info["data"]},
                options=options,
            )

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
                options[CONF_NUMBER_OF_PHASES] = int(user_input[CONF_NUMBER_OF_PHASES])
                options[CONF_USE_SLIDERS] = bool(user_input[CONF_USE_SLIDERS])
                options[CONF_AC_SYSTEM_VOLTAGE] = int(
                    user_input[CONF_AC_SYSTEM_VOLTAGE]
                )
                options[CONF_DC_SYSTEM_VOLTAGE] = int(
                    user_input[CONF_DC_SYSTEM_VOLTAGE]
                )

                try:
                    info = await validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except HomeAssistantError:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                _LOGGER.debug("setting up extra entry")
                return self.async_create_entry(
                    title=info["title"],
                    data={SCAN_REGISTERS: info["data"]},
                    options=options,
                )

        return self.async_show_form(
            step_id="advanced",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AC_SYSTEM_VOLTAGE, default=str(AC_VOLTAGES["US (120)"])
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in AC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(
                        CONF_NUMBER_OF_PHASES,
                        default=str(PHASE_CONFIGURATIONS["single phase"]),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in PHASE_CONFIGURATIONS.items()
                            ]
                        ),
                    ),
                    vol.Required(CONF_AC_CURRENT_LIMIT, default=0): vol.All(
                        vol.Coerce(int, "must be a number")
                    ),
                    vol.Required(
                        CONF_DC_SYSTEM_VOLTAGE, default=str(DC_VOLTAGES["lifepo4_12v"])
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in DC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(CONF_DC_CURRENT_LIMIT, default=0): vol.All(
                        vol.Coerce(int, "must be a number")
                    ),
                    vol.Optional(CONF_USE_SLIDERS, default=True): bool,
                }
            ),
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Add reconfigure step to allow to reconfigure a config entry."""
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        errors = {}

        if user_input is not None:
            try:
                hub = VictronHub(user_input[CONF_HOST], user_input[CONF_PORT])
                await hub.connect()
                _LOGGER.info("connection was succesfull")
            except HomeAssistantError as e:
                errors["base"] = f"cannot_connect ({e!s})"

            else:
                new_options = config_entry.options | {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                }
                return self.async_update_reload_and_abort(
                    config_entry,
                    title=DOMAIN,
                    options=new_options,
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=config_entry.options[CONF_HOST]
                    ): str,
                    vol.Required(
                        CONF_PORT, default=config_entry.options[CONF_PORT]
                    ): int,
                }
            ),
            errors=errors,
        )


class parsedEntry:
    """Parsed entry."""

    def __init__(self, decoderInfo: RegisterInfo, value):
        """Initialize the parsed entry."""
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
        # combine dictionaries with priority given to user_input
        dict_priority = {1: user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]}
        return self.async_create_entry(title="", data=combined_config)

    async def async_step_init_read(self, user_input=None):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        # combine dictionaries with priority given to user_input
        if user_input[CONF_RESCAN]:
            info = await validate_input(self.hass, config)
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={SCAN_REGISTERS: info["data"]}, title=""
            )

        user_input.pop(CONF_RESCAN, None)
        dict_priority = {1: user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]}

        if user_input[CONF_ADVANCED_OPTIONS]:
            self.hass.config_entries.async_update_entry(
                self.config_entry, options=combined_config, title=""
            )
            _LOGGER.debug("returning step init because advanced options were selected")
            errors = {}
            # move to dedicated function (the write show form) to allow for re-use
            return self.init_write_form(errors)
        return self.async_create_entry(title="", data=combined_config)

    async def async_step_init_write(self, user_input=None):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        # remove temp options =
        if user_input[CONF_RESCAN]:
            info = await validate_input(self.hass, config)
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={SCAN_REGISTERS: info["data"]}, title=""
            )

        user_input.pop(CONF_RESCAN, None)
        # combine dictionaries with priority given to user_input
        dict_priority = {1: user_input, 2: config}
        combined_config = {**dict_priority[2], **dict_priority[1]}

        if not user_input[CONF_ADVANCED_OPTIONS]:
            self.hass.config_entries.async_update_entry(
                self.config_entry, options=combined_config, title=""
            )
            _LOGGER.debug("returning step init because advanced options were selected")
            errors = {}
            # move to dedicated function (the write show form) to allow for re-use
            return self.init_read_form(errors)

        return self.async_create_entry(title="", data=combined_config)

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
                    # config[SCAN_REGISTERS] = info["data"]
                    _LOGGER.debug(info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except HomeAssistantError:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if user_input[CONF_RESCAN]:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={SCAN_REGISTERS: info["data"]}, title=""
                )
            # return self.async_create_entry(title="", data={})

            return self.async_create_entry(title="", data=config)

        if config[CONF_ADVANCED_OPTIONS]:
            _LOGGER.debug("advanced options is set")

            return self.init_write_form(errors)
        if user_input is None:
            return self.init_read_form(errors)
        return None

    def init_read_form(self, errors: dict):
        """Handle read support and limit settings if requested."""
        return self.async_show_form(
            step_id="init_read",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INTERVAL, default=self.config_entry.options[CONF_INTERVAL]
                    ): vol.All(vol.Coerce(int)),
                    vol.Optional(CONF_RESCAN, default=False): bool,
                    vol.Optional(CONF_ADVANCED_OPTIONS, default=False): bool,
                },
            ),
        )

    def init_write_form(self, errors: dict):
        """Handle write support and limit settings if requested."""
        config = dict(self.config_entry.options)
        system_ac_voltage_default = self.config_entry.options.get(
            CONF_AC_SYSTEM_VOLTAGE, AC_VOLTAGES["US (120)"]
        )
        system_dc_voltage_default = self.config_entry.options.get(
            CONF_DC_SYSTEM_VOLTAGE, DC_VOLTAGES["lifepo4_12v"]
        )
        system_number_of_phases_default = self.config_entry.options.get(
            CONF_NUMBER_OF_PHASES, PHASE_CONFIGURATIONS["single phase"]
        )
        errors = {}
        return self.async_show_form(
            step_id="init_write",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INTERVAL, default=self.config_entry.options[CONF_INTERVAL]
                    ): vol.All(vol.Coerce(int)),
                    vol.Required(
                        CONF_AC_SYSTEM_VOLTAGE, default=str(system_ac_voltage_default)
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in AC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(
                        CONF_NUMBER_OF_PHASES,
                        default=str(system_number_of_phases_default),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in PHASE_CONFIGURATIONS.items()
                            ]
                        ),
                    ),
                    vol.Required(
                        CONF_AC_CURRENT_LIMIT,
                        default=config.get(CONF_AC_CURRENT_LIMIT, 1),
                    ): vol.All(
                        vol.Coerce(
                            int, "must be the max current of a single phase as a number"
                        )
                    ),
                    vol.Required(
                        CONF_DC_SYSTEM_VOLTAGE, default=str(system_dc_voltage_default)
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=str(value), label=key)
                                for key, value in DC_VOLTAGES.items()
                            ]
                        ),
                    ),
                    vol.Required(
                        CONF_DC_CURRENT_LIMIT,
                        default=config.get(CONF_DC_CURRENT_LIMIT, 1),
                    ): vol.All(
                        vol.Coerce(
                            int,
                            "must be the total DC current for the system as a number",
                        )
                    ),
                    vol.Optional(
                        CONF_USE_SLIDERS,
                        default=config.get(
                            CONF_USE_SLIDERS, config.get(CONF_USE_SLIDERS, True)
                        ),
                    ): bool,
                    vol.Optional(CONF_RESCAN, default=False): bool,
                    vol.Optional(CONF_ADVANCED_OPTIONS, default=True): bool,
                },
            ),
        )

    @staticmethod
    def get_dict_key(dict, val):
        """Get the key from a dictionary."""
        for key, value in dict.items():
            if val == value:
                return key

        return "key doesn't exist"


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
