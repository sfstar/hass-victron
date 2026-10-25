"""The victron integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_INTERVAL, CONF_PORT, DOMAIN, SCAN_REGISTERS
from .coordinator import victronEnergyDeviceUpdateCoordinator as Coordinator
from .hub import VictronHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def _revalidate_stored_registers(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Heal stored register set against current detection rules at startup.

    Existing config entries can carry register blocks detected before
    determine_present_devices learned to validate TextReadEntityType
    contents. Re-probe each stored block (with multi-read consensus in
    the hub) and drop ones whose text registers consistently fail to
    decode. Blocks that error on every probe attempt -- e.g. device is
    transiently unreachable -- are kept in place so a temporary outage
    cannot wipe a working configuration.

    Wrapped in a broad exception handler: failures here must not break
    integration startup, since the existing stored config will still
    serve fine on its own.

    Runs before the update_listener is registered, so the
    async_update_entry call does not trigger a reload.
    """
    stored = config_entry.data.get(SCAN_REGISTERS) or {}
    if not stored:
        return

    try:
        hub = VictronHub(
            config_entry.options[CONF_HOST], config_entry.options[CONF_PORT]
        )
        try:
            connected = await hass.async_add_executor_job(hub.connect)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug(
                "Skipping register revalidation: hub.connect raised %s", err
            )
            return
        if not connected:
            _LOGGER.debug("Skipping register revalidation: hub did not connect")
            return
        try:
            pruned = await hass.async_add_executor_job(
                hub.revalidate_register_set, stored
            )
        finally:
            try:
                await hass.async_add_executor_job(hub.disconnect)
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Hub disconnect after revalidation raised %s", err)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "Register revalidation failed: %s; using stored config", err
        )
        return

    if pruned == stored:
        return

    new_data = {**config_entry.data, SCAN_REGISTERS: pruned}
    hass.config_entries.async_update_entry(config_entry, data=new_data)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up victron from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    await _revalidate_stored_registers(hass, config_entry)

    coordinator = Coordinator(
        hass,
        config_entry.options[CONF_HOST],
        config_entry.options[CONF_PORT],
        config_entry.data[SCAN_REGISTERS],
        config_entry.options[CONF_INTERVAL],
    )
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
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)
