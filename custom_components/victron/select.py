"""Support for Victron energy switches."""

from __future__ import annotations

from datetime import timedelta
from enum import Enum
import logging
from typing import Any, dataclass_transform

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
from .coordinator import VictronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up victron select devices."""
    victron_coordinator: VictronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][
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
                    if isinstance(registerInfo.entity_type, SelectWriteType):
                        _LOGGER.debug(
                            "unit == %s registerLedger == %s register_info",
                            slave,
                            registerLedger,
                        )

                        description = VictronEntityDescription(
                            key=register_name,
                            name=register_name.replace("_", " "),
                            slave=slave,
                            options=registerInfo.entity_type.options,
                            address=registerInfo.register,
                        )

                        descriptions.append(description)
                        _LOGGER.debug("composed description == %s", description)

    entities = [
        VictronSelect(hass, victron_coordinator, description)
        for description in descriptions
    ]

    _LOGGER.debug("adding selects")
    _LOGGER.debug(entities)
    async_add_entities(entities)


@dataclass_transform(frozen_default=True)
class VictronEntityDescription(
    SelectEntityDescription,  # type: ignore[misc]
    VictronWriteBaseEntityDescription,
):
    """Describes victron sensor entity."""

    options: type[Enum] = Enum


class VictronSelect(CoordinatorEntity, SelectEntity):  # type: ignore[misc]
    """Representation of a Victron switch."""

    description: VictronEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: VictronEnergyDeviceUpdateCoordinator,
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
            self.entity_id = f"{SELECT_DOMAIN}.{DOMAIN}_{self.description.key}_{self.description.slave}"
        else:
            self.entity_id = f"{SELECT_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update: bool
        super().__init__(coordinator)

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        _LOGGER.debug("select_async_update")
        try:
            self._attr_native_value = self.description.value_fn(  # type: ignore[call-arg]
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
            self._unsub_update()  # type: ignore[misc]
            self._unsub_update = None  # type: ignore[assignment]

        # Schedule the next update at exactly the next whole hour sharp
        self._unsub_update = event.async_track_point_in_utc_time(
            self.hass,
            self._update_job,
            utcnow() + timedelta(seconds=self.coordinator.interval),
        )

    @property
    def current_option(self) -> Any:
        """Return the currently selected option."""
        return self.description.options(
            self.description.value_fn(  # type: ignore[call-arg]
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
    def available(self) -> Any:
        """Return True if entity available."""
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
