"""Support for victron energy switches."""

from __future__ import annotations

import logging
from typing import Any, cast, dataclass_transform

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
from .coordinator import VictronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up victron switch devices."""
    victron_coordinator: VictronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    _LOGGER.debug("attempting to setup switch entities")
    descriptions = []
    # TODO cleanup
    if config_entry.options[CONF_ADVANCED_OPTIONS]:
        register_set = victron_coordinator.processed_data()["register_set"]
        for slave, register_ledger in register_set.items():
            for name in register_ledger:
                for register_name, register_info in register_info_dict[name].items():
                    _LOGGER.debug(
                        "unit == %s register_ledger == %s register_info == %s",
                        slave,
                        register_ledger,
                        register_info,
                    )

                    if isinstance(register_info.entity_type, SwitchWriteType):
                        description = VictronEntityDescription(
                            key=register_name,
                            name=register_name.replace("_", " "),
                            slave=slave,
                            address=register_info.register,
                        )
                        descriptions.append(description)
                        _LOGGER.debug("composed description == %s", description)

    entities = [
        VictronSwitch(hass, victron_coordinator, description)
        for description in descriptions
    ]

    _LOGGER.debug("adding switches")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass_transform(frozen_default=True)
class VictronEntityDescription(
    SwitchEntityDescription,  # type: ignore[misc]
    VictronWriteBaseEntityDescription,
):
    """Describes victron sensor entity."""


class VictronSwitch(CoordinatorEntity, SwitchEntity):  # type: ignore[misc]
    """Representation of a Victron switch."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: VictronEnergyDeviceUpdateCoordinator,
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
                f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}_{description.slave}"
            )
        else:
            self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{self.description.key}"

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
        data = self.description.value_fn(  # type: ignore[call-arg]
            self.coordinator.processed_data(),
            self.description.slave,
            self.description.key,
        )
        return cast(bool, data)

    @property
    def available(self) -> Any:
        """Return True if entity is available."""
        full_key = str(self.description.slave) + "." + self.description.key
        return self.coordinator.processed_data()["availability"][full_key]

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return the device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.unique_id.split("_")[0])},
            name=self.unique_id.split("_")[1],
            model=self.unique_id.split("_", maxsplit=1)[0],
            manufacturer="victron",
        )
