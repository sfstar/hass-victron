"""Support for Victron energy button sensors."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import (
    DOMAIN as BUTTON_DOMAIN,
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base import VictronWriteBaseEntityDescription
from .const import CONF_ADVANCED_OPTIONS, DOMAIN, ButtonWriteType, register_info_dict
from .coordinator import VictronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victron energy binary sensor entries."""
    _LOGGER.debug("attempting to setup button entities")
    victron_coordinator: VictronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    descriptions = []
    # TODO cleanup
    register_set: Any = victron_coordinator.processed_data()["register_set"]
    for slave, registerLedger in register_set.items():
        for name in registerLedger:
            for register_name, registerInfo in register_info_dict[name].items():
                _LOGGER.debug(
                    "unit == %s registerLedger == %s register_info",
                    slave,
                    registerLedger,
                )
                if not config_entry.options[CONF_ADVANCED_OPTIONS]:
                    continue

                if isinstance(registerInfo.entity_type, ButtonWriteType):
                    description = VictronEntityDescription(
                        key=register_name,
                        name=register_name.replace("_", " "),
                        slave=slave,
                        device_class=ButtonDeviceClass.RESTART,
                        address=registerInfo.register,
                    )
                    _LOGGER.debug("composed description == %s", description)
                    descriptions.append(description)

    _entities = []
    _entity: dict = {}
    for description in descriptions:
        _entity = description
        _entities.append(VictronBinarySensor(victron_coordinator, _entity))

    async_add_entities(_entities, True)


@dataclass(frozen=True)
class VictronEntityDescription(
    ButtonEntityDescription,  # type: ignore[misc]
    VictronWriteBaseEntityDescription,
):
    """Describes victron sensor entity."""


class VictronBinarySensor(CoordinatorEntity, ButtonEntity):  # type: ignore[misc]
    """A button implementation for Victron energy device."""

    def __init__(
        self,
        coordinator: VictronEnergyDeviceUpdateCoordinator,
        description: VictronEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.description: VictronEntityDescription = description
        self._attr_device_class = description.device_class
        self._attr_name = f"{description.name}"

        self._attr_unique_id = f"{self.description.slave}_{self.description.key}"
        if self.description.slave not in (100, 225):
            self.entity_id = f"{BUTTON_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.slave}"
        else:
            self.entity_id = f"{BUTTON_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    async def async_press(self) -> None:
        """Handle the button press."""
        self.coordinator.write_register(
            unit=self.description.slave, address=self.description.address, value=1
        )

    @property
    def available(self) -> Any:
        """Return True if entity available."""
        full_key = str(self.description.slave) + "." + self.description.key
        return self.coordinator.processed_data()["availability"][full_key]

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return the device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.unique_id.split("_", maxsplit=1)[0])},
            name=self.unique_id.split("_", maxsplit=1)[1],
            model=self.unique_id.split("_", maxsplit=1)[0],
            manufacturer="victron",
        )
