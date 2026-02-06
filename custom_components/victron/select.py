"""Support for Victron energy switches."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import logging

from homeassistant.components.select import (
    DOMAIN as SELECT_DOMAIN,
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import entity, event
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import utcnow

from .base import VictronWriteBaseEntityDescription
from .const import CONF_ADVANCED_OPTIONS, DOMAIN, SelectWriteType, register_info_dict
from .coordinator import victronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up victron select devices."""
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    _LOGGER.debug("attempting to setup select entities")
    descriptions = []
    # TODO cleanup
    if config_entry.options[CONF_ADVANCED_OPTIONS]:
        register_set = victron_coordinator.processed_data()["register_set"]
        for slave, registerLedger in register_set.items():
            for name in registerLedger:
                for register_name, registerInfo in register_info_dict[name].items():
                    if isinstance(registerInfo.entityType, SelectWriteType):
                        _LOGGER.debug(
                            "unit == %s registerLedger == %s registerInfo",
                            slave,
                            registerLedger,
                        )

                        description = VictronEntityDescription(
                            key=register_name,
                            name=register_name.replace("_", " "),
                            slave=slave,
                            options=registerInfo.entityType.options,
                            address=registerInfo.register,
                        )

                        descriptions.append(description)
                        _LOGGER.debug("composed description == %s", description)

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(VictronSelect(hass, victron_coordinator, entity))
    _LOGGER.debug("adding selects")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass
class VictronEntityDescription(
    SelectEntityDescription, VictronWriteBaseEntityDescription
):
    """Describes victron sensor entity."""

    options: Enum = None


class VictronSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Victron switch."""

    description: VictronEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: victronEnergyDeviceUpdateCoordinator,
        description: VictronEntityDescription,
    ) -> None:
        """Initialize the select."""
        self._attr_native_value = None
        _LOGGER.debug("select init")
        self.coordinator = coordinator
        self.description: VictronEntityDescription = description
        # this needs to be changed to allow multiple of the same type
        self._attr_name = f"{description.name}"

        self._attr_unique_id = f"{self.description.slave}_{self.description.key}"
        if self.description.slave not in (100, 225):
            self.entity_id = f"{SELECT_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.slave}".lower()
        else:
            self.entity_id = f"{SELECT_DOMAIN}.{DOMAIN}_{self.description.key}".lower()

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None
        super().__init__(coordinator)

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        _LOGGER.debug("select_async_update")
        try:
            self._attr_native_value = self.description.value_fn(
                self.coordinator.processed_data(),
                self.description.slave,
                self.description.key,
            )
        except (TypeError, IndexError):
            _LOGGER.debug("failed to retrieve value")
            # No data available
            self._attr_native_value = None

        # Cancel the currently scheduled event if there is any
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

        # Schedule the next update at exactly the next whole hour sharp
        self._unsub_update = event.async_track_point_in_utc_time(
            self.hass,
            self._update_job,
            utcnow() + timedelta(seconds=self.coordinator.interval),
        )

    @property
    def current_option(self) -> str:
        """Return the currently selected option."""
        return self.description.options(
            self.description.value_fn(
                self.coordinator.processed_data(),
                self.description.slave,
                self.description.key,
            )
        ).name

    @property
    def options(self) -> list:
        """Return a list of available options."""
        return [option.name for option in self.description.options]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self.coordinator.write_register(
            unit=self.description.slave,
            address=self.description.address,
            value=self.coordinator.encode_scaling(
                int(self.description.options[option].value), "", 0
            ),
        )

    # TODO extract these type of property definitions to base class
    @property
    def available(self) -> bool:
        """Return True if entity available."""
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
