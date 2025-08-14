"""The Victron GX modbusTCP integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_INTERVAL, CONF_PORT, DOMAIN, SCAN_REGISTERS
from .coordinator import VictronEnergyDeviceUpdateCoordinator as Coordinator
# For your initial PR, limit it to 1 platform.
# There will be also: SWITCH, NUMBER, SELECT, BINARY_SENSOR, BUTTON
_PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up victron from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    coordinator_ = Coordinator(
        hass,
        config_entry.options[CONF_HOST],
        config_entry.options[CONF_PORT],
        config_entry.data[SCAN_REGISTERS],
        config_entry.options[CONF_INTERVAL],
    )

    # Finalize
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator_

    await coordinator_.async_config_entry_first_refresh()
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    config_entry.runtime_data = coordinator_
    await hass.config_entries.async_forward_entry_setups(config_entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, _PLATFORMS
    ):
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)
