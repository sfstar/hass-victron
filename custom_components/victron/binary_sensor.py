"""Support for Victron Energy binary sensors."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import cast

from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base import VictronBaseEntityDescription
from .const import DOMAIN, BoolReadEntityType, register_info_dict
from .coordinator import victronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victron energy binary sensor entries."""
    _LOGGER.debug("attempting to setup binary sensor entities")
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    _LOGGER.debug(victron_coordinator.processed_data()["register_set"])
    _LOGGER.debug(victron_coordinator.processed_data()["data"])
    descriptions = []
    # TODO cleanup
    register_set = victron_coordinator.processed_data()["register_set"]
    for slave, registerLedger in register_set.items():
        for name in registerLedger:
            for register_name, registerInfo in register_info_dict[name].items():
                _LOGGER.debug(
                    "unit == %s registerLedger == %s registerInfo",
                    slave,
                    registerLedger,
                )

                if isinstance(registerInfo.entityType, BoolReadEntityType):
                    description = VictronEntityDescription(
                        key=register_name,
                        name=register_name.replace("_", " "),
                        slave=slave,
                    )
                    _LOGGER.debug("composed description == %s", description)
                    descriptions.append(description)

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(VictronBinarySensor(victron_coordinator, entity))

    async_add_entities(entities, True)


@dataclass
class VictronEntityDescription(
    BinarySensorEntityDescription, VictronBaseEntityDescription
):
    """Describes victron sensor entity."""


class VictronBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """A binary sensor implementation for Victron energy device."""

    def __init__(
        self,
        coordinator: victronEnergyDeviceUpdateCoordinator,
        description: VictronEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        self.description: VictronEntityDescription = description
        # this needs to be changed to allow multiple of the same type
        self._attr_device_class = description.device_class
        self._attr_name = f"{description.name}"

        self._attr_unique_id = f"{self.description.slave}_{self.description.key}"
        if self.description.slave not in (100, 225):
            self.entity_id = f"{BINARY_SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.slave}".lower()
        else:
            self.entity_id = f"{BINARY_SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}".lower()

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
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
