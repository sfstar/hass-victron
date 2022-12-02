"""Support for Victron energy button sensors."""
from __future__ import annotations

from contextlib import suppress
from typing import cast

from homeassistant.core import HomeAssistant, HassJob

from collections.abc import Callable
from homeassistant.helpers.typing import StateType

from dataclasses import dataclass

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import event, entity

from homeassistant.components.button import ButtonEntityDescription, ButtonEntity, DOMAIN as BUTTON_DOMAIN

from .coordinator import victronEnergyDeviceUpdateCoordinator

from .const import DOMAIN, CONF_ADVANCED_OPTIONS, register_info_dict, ButtonWriteType

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victron energy binary sensor entries."""
    _LOGGER.debug("attempting to setup button entities")
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug(victron_coordinator.processed_data()["register_set"])
    _LOGGER.debug(victron_coordinator.processed_data()["data"])
    descriptions = []
    #TODO cleanup
    register_set = victron_coordinator.processed_data()["register_set"]
    for unit, registerLedger in register_set.items():
        for name in registerLedger:
            for register_name, registerInfo in register_info_dict[name].items():
                # _LOGGER.debug("unit == " + str(unit) + " registerLedger == " + str(registerLedger) + " registerInfo ")
                # _LOGGER.debug(str(registerInfo.unit))
                if config_entry.options[CONF_ADVANCED_OPTIONS]:
                    if not isinstance(registerInfo.entityType, ButtonWriteType): #TODO change to button
                        continue


                descriptions.append(VictronEntityDescription(
                    key=register_name,
                    name=register_name.replace('_', ' '),
                    value_fn=lambda data: data["data"][unit + "." + register_name],
                    unit=unit,
                    # device_class=None, #determine_victron_device_class(register_name, registerInfo.unit),
                ))

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(
            VictronBinarySensor(
                victron_coordinator,
                entity
                ))

    async_add_entities(
        entities, True
    )


@dataclass
class VictronEntityDescription(ButtonEntityDescription):
    """Describes victron sensor entity."""
    #TODO write unit references into this class and convert to base for all entity types
    unit: int = None
    value_fn: Callable[[dict], StateType] = None

class VictronBinarySensor(CoordinatorEntity, ButtonEntity):
    """A button implementation for Victron energy device."""
    # TODO determine in other method
    # _attr_attribution = ATTRIBUTION
    # _attr_icon = ICON
    # _attr_device_class = SensorDeviceClass.MONETARY


    def __init__(self, coordinator: victronEnergyDeviceUpdateCoordinator, description: VictronEntityDescription) -> None:
        """Initialize the sensor."""
        self.description: VictronEntityDescription = description
        #this needs to be changed to allow multiple of the same type
        self._attr_device_class = description.device_class
        self._attr_name = f"{description.name}"
        self.data_key = str(self.description.unit) + "." + str(self.description.key)

        self._attr_unique_id = f"{description.unit}_{self.description.key}"
        if description.unit not in (100, 225):
            self.entity_id = f"{BUTTON_DOMAIN}.{DOMAIN}_{self.description.key}_{description.unit}"
        else:
            self.entity_id = f"{BUTTON_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    async def async_press(self) -> None:
        """Handle the button press."""
        self.coordinator.write_register(unit=self.description.unit, address=register_info_dict[self.description.register_ledger_key][self.description.key].register, value=1)

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
            manufacturer="victron", # to be dynamically set for gavazzi and redflow
        )