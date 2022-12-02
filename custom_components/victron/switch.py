"""Support for victron energy switches."""
from __future__ import annotations

from typing import Any, cast

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription, DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, HassJob
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import victronEnergyDeviceUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity

from .const import DOMAIN, register_info_dict, SwitchWriteType, CONF_ADVANCED_OPTIONS
from .base import VictronWriteBaseEntityDescription

from collections.abc import Callable
from homeassistant.helpers.typing import StateType

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up victron switch devices."""
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("attempting to setup switch entities")
    descriptions = []
    #TODO cleanup
    if config_entry.options[CONF_ADVANCED_OPTIONS]:
        register_set = victron_coordinator.processed_data()["register_set"]
        for slave, registerLedger in register_set.items():
            for name in registerLedger:
                for register_name, registerInfo in register_info_dict[name].items():
                    # _LOGGER.debug("unit == " + str(unit) + " registerLedger == " + str(registerLedger) + " registerInfo ")
                    # _LOGGER.debug(str(registerInfo.unit))
                    # _LOGGER.debug("register_name")
                    # _LOGGER.debug(register_name)
                    if isinstance(registerInfo.entityType, SwitchWriteType):
                        descriptions.append(VictronEntityDescription(
                            key=register_name,
                            name=register_name.replace('_', ' '),
                            value_fn=lambda data: data["data"][register_name],
                            slave=slave,
                            address=registerInfo.register,
                        ))

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(
            VictronSwitch(
                hass,
                victron_coordinator,
                entity
                ))
    _LOGGER.debug("adding switches")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass
class VictronEntityDescription(SwitchEntityDescription, VictronWriteBaseEntityDescription):
    """Describes victron sensor entity."""

class VictronSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Victron switch."""

    def __init__(self, hass: HomeAssistant, coordinator: victronEnergyDeviceUpdateCoordinator, description: VictronEntityDescription) -> None:
        self.coordinator = coordinator
        self.description: VictronEntityDescription = description
        #this needs to be changed to allow multiple of the same type
        self._attr_name = f"{description.name}"
        self.data_key = str(self.description.slave) + "." + str(self.description.key)

        self._attr_unique_id = f"{self.description.slave}_{self.description.key}"
        if self.description.slave not in (100, 225):
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.slave}"
        else:
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None
        super().__init__(coordinator)


    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        self.coordinator.write_register(unit=self.description.slave, address=self.description.address, value=1)
        await self.coordinator.async_update_local_entry(self.data_key, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        self.coordinator.write_register(unit=self.description.slave, address=self.description.address, value=0)
        await self.coordinator.async_update_local_entry(self.data_key, 0)

    @property
    def is_on(self) -> bool:
        data = self.coordinator.processed_data()["data"][self.data_key]
        """Return true if switch is on."""
        return cast(bool, data)

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return the device info."""
        return entity.DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id.split('_')[0])
            },
            name=self.unique_id.split('_')[1],
            model=self.unique_id.split('_')[0],
            manufacturer="victron",
        )