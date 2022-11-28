"""The victron integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOST, CONF_PORT, SCAN_REGISTERS, CONF_INTERVAL
from .coordinator import victronEnergyDeviceUpdateCoordinator as Coordinator

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up victron from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    #TODO group register sets in devices
    coordinator = Coordinator(hass, entry.options[CONF_HOST], entry.options[CONF_PORT], entry.options[SCAN_REGISTERS], entry.options[CONF_INTERVAL]) # TODO static first index reference needs to be changed for dynamic support
    # try:
    #     await coordinator.async_config_entry_first_refresh()
    # except ConfigEntryNotReady:
    #     await coordinator.api.close()
    #     raise

    # Finalize
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
