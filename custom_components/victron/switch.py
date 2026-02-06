"""Support for victron energy switches."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, cast

from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base import VictronWriteBaseEntityDescription
from .const import CONF_ADVANCED_OPTIONS, DOMAIN, SwitchWriteType, register_info_dict
from .coordinator import victronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up victron switch devices."""
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    _LOGGER.debug("attempting to setup switch entities")
    descriptions = []
    # TODO cleanup
    if config_entry.options[CONF_ADVANCED_OPTIONS]:
        register_set = victron_coordinator.processed_data()["register_set"]
        for slave, registerLedger in register_set.items():
            for name in registerLedger:
                for register_name, registerInfo in register_info_dict[name].items():
                    _LOGGER.debug(
                        "unit == %s registerLedger == %s registerInfo == %s",
                        slave,
                        registerLedger,
                        registerInfo,
                    )

                    if isinstance(registerInfo.entityType, SwitchWriteType):
                        description = VictronEntityDescription(
                            key=register_name,
                            name=register_name.replace("_", " "),
                            slave=slave,
                            address=registerInfo.register,
                        )
                        descriptions.append(description)
                        _LOGGER.debug("composed description == %s", description)

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(VictronSwitch(hass, victron_coordinator, entity))
    _LOGGER.debug("adding switches")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass
class VictronEntityDescription(
    SwitchEntityDescription, VictronWriteBaseEntityDescription
):
    """Describes victron sensor entity."""


class VictronSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Victron switch."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: victronEnergyDeviceUpdateCoordinator,
        description: VictronEntityDescription,
    ) -> None:
        """Initialize the switch."""
        self.coordinator = coordinator
        self.description: VictronEntityDescription = description
        self._attr_name = f"{description.name}"
        self.data_key = str(self.description.slave) + "." + str(self.description.key)

        self._attr_unique_id = f"{description.slave}_{self.description.key}"
        if description.slave not in (100, 225):
            self.entity_id = (
                f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}_{description.slave}".lower()
            )
        else:
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}".lower()

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None
        super().__init__(coordinator)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        self.coordinator.write_register(
            unit=self.description.slave, address=self.description.address, value=1
        )
        await self.coordinator.async_update_local_entry(self.data_key, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        self.coordinator.write_register(
            unit=self.description.slave, address=self.description.address, value=0
        )
        await self.coordinator.async_update_local_entry(self.data_key, 0)

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        data = self.description.value_fn(
            self.coordinator.processed_data(),
            self.description.slave,
            self.description.key,
        )
        return cast("bool", data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        full_key = str(self.description.slave) + "." + self.description.key
        return self.coordinator.processed_data()["availability"][full_key]

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return the device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.unique_id.split("_")[0])},
            name=self.unique_id.split("_")[1],
            model=self.unique_id.split("_")[0],
            manufacturer="victron",
        )
