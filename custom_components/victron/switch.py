"""Support for Abode Security System switches."""
from __future__ import annotations

from typing import Any, cast

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription, DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, HassJob
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import victronEnergyDeviceUpdateCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, register_info_dict, SwitchWriteType

from collections.abc import Callable
from homeassistant.helpers.typing import StateType

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Abode switch devices."""
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("attempting to setup switch entities")
    descriptions = []
    #TODO cleanup
    register_set = victron_coordinator.processed_data()["register_set"]
    for unit, registerLedger in register_set.items():
        for name in registerLedger:
            for register_name, registerInfo in register_info_dict[name].items():
                _LOGGER.debug("unit == " + str(unit) + " registerLedger == " + str(registerLedger) + " registerInfo ")
                _LOGGER.debug(str(registerInfo.unit))
                _LOGGER.debug("register_name")
                _LOGGER.debug(register_name)
                if isinstance(registerInfo.writeType, SwitchWriteType):
                    descriptions.append(VictronEntityDescription(
                        key=register_name,
                        name=register_name.replace('_', ' '),
                        value_fn=lambda data: data["data"][register_name].value,
                        unit=unit,
                        register_ledger_key=name
                    ))

    # for key in victron_coordinator.processed_data()["register_set"]:
    #     for register_name, registerInfo in register_info_dict[key].items():
        
    #         if isinstance(registerInfo.writeType, SwitchWriteType):
    #             _LOGGER.debug("switch entity")
    #             _LOGGER.debug(register_name)
    #             _LOGGER.debug(registerInfo)
    #             _LOGGER.debug(key)
    #             descriptions.append(VictronEntityDescription(
    #                 key=register_name,
    #                 name=register_name.replace('_', ' '),
    #                 value_fn=lambda data: data["data"][register_name].value,
    #                 unit=unit
    #             ))

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(
            VictronSwitch(
                victron_coordinator,
                entity
                ))
    _LOGGER.debug("adding switches")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass
class VictronEntityDescription(SwitchEntityDescription):
    """Describes victron sensor entity."""
    #TODO write unit references into this class and convert to base for all entity types
    unit: int = None
    value_fn: Callable[[dict], StateType] = None
    register_ledger_key: str = None

class VictronSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Victron switch."""

    def __init__(self, coordinator: victronEnergyDeviceUpdateCoordinator, description: VictronEntityDescription) -> None:
        self.coordinator = coordinator
        self.description: VictronEntityDescription = description
        #this needs to be changed to allow multiple of the same type
        self._attr_name = f"{description.name}"
        self.data_key = str(self.description.unit + "." + self.description.key)

        self._attr_unique_id = f"{self.description.unit}_{self.description.key}"
        if self.description.unit not in (100, 225):
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.unit}"
        else:
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None
        super().__init__(coordinator)


    def turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        self.coordinator.write_register(unit=self.description.unit, address=register_info_dict[self.description.register_ledger_key][self.description.key].register, value=1)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        #TODO fix bouncing toggle due to data not directly being updated after this action
        self.coordinator.write_register(unit=self.description.unit, address=register_info_dict[self.description.register_ledger_key][self.description.key].register, value=0)
        

    @property
    def is_on(self) -> bool:
        #TODO see if entitydescription can be updated to include unit info and set it in init
        data = self.coordinator.processed_data()["data"][self.data_key]
        self._attr_native_value = data.value
        """Return true if switch is on."""
        return cast(bool, data.value)
