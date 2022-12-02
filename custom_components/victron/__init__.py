"""The victron integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOST, CONF_PORT, SCAN_REGISTERS, CONF_INTERVAL, CONF_AC_SYSTEM_VOLTAGE, CONF_AC_CURRENT_LIMIT, CONF_DC_SYSTEM_VOLTAGE, CONF_DC_CURRENT_LIMIT
from .coordinator import victronEnergyDeviceUpdateCoordinator as Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT, Platform.BINARY_SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up victron from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    coordinator = Coordinator(hass, config_entry.options[CONF_HOST], config_entry.options[CONF_PORT], 
                                       config_entry.data[SCAN_REGISTERS], config_entry.options[CONF_INTERVAL])
    # try:
    #     await coordinator.async_config_entry_first_refresh()
    # except ConfigEntryNotReady:
    #     await coordinator.api.close()
    #     raise

    # Finalize
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)