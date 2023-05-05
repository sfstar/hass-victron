"""Support for Victron energy sensors."""

from dataclasses import dataclass

import logging

from datetime import timedelta
from homeassistant.util import utcnow
from homeassistant.helpers import event, entity
from homeassistant.core import HomeAssistant, HassJob
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorEntity, DOMAIN as SENSOR_DOMAIN

from .coordinator import victronEnergyDeviceUpdateCoordinator
from .base import VictronBaseEntityDescription
from .const import DOMAIN, register_info_dict, CONF_ADVANCED_OPTIONS, ReadEntityType, TextReadEntityType, BoolReadEntityType

from homeassistant.const import (
    PERCENTAGE, 
    UnitOfEnergy, 
    UnitOfPower,
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_CURRENT_AMPERE,
    FREQUENCY_HERTZ,
    TIME_SECONDS,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfSpeed,
    UnitOfPressure
)

from collections.abc import Callable
from homeassistant.helpers.typing import StateType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victron energy sensor entries."""
    _LOGGER.debug("attempting to setup sensor entities")
    victron_coordinator: victronEnergyDeviceUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug(victron_coordinator.processed_data()["register_set"])
    _LOGGER.debug(victron_coordinator.processed_data()["data"])
    descriptions = []
    #TODO cleanup
    register_set = victron_coordinator.processed_data()["register_set"]
    for slave, registerLedger in register_set.items():
        for name in registerLedger:
            for register_name, registerInfo in register_info_dict[name].items():
                # _LOGGER.debug("unit == " + str(slave) + " registerLedger == " + str(registerLedger) + " registerInfo ")
                # _LOGGER.debug(str(registerInfo.slave))
                if config_entry.options[CONF_ADVANCED_OPTIONS]:
                    if not isinstance(registerInfo.entityType, ReadEntityType) or isinstance(registerInfo.entityType, BoolReadEntityType):
                        continue


                descriptions.append(VictronEntityDescription(
                    key=register_name,
                    name=register_name.replace('_', ' '),
                    native_unit_of_measurement=registerInfo.unit,
                    state_class=registerInfo.determine_stateclass(),
                    slave=slave,
                    device_class=determine_victron_device_class(register_name, registerInfo.unit),
                    entity_type=registerInfo.entityType if isinstance(registerInfo.entityType, TextReadEntityType) else None
                ))

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(
            VictronSensor(
                victron_coordinator,
                entity
                ))

    # Add an entity for each sensor type
    async_add_entities(entities, True)

def determine_victron_device_class(name, unit):
    if unit == PERCENTAGE:
        return SensorDeviceClass.BATTERY
    elif unit in [member.value for member in UnitOfPower]:
        return SensorDeviceClass.POWER
    elif unit in [member.value for member in UnitOfEnergy]:
        _LOGGER.debug("unit of energy")
        return SensorDeviceClass.ENERGY
    elif unit == FREQUENCY_HERTZ:
        return SensorDeviceClass.FREQUENCY
    elif unit == TIME_SECONDS:
        return SensorDeviceClass.DURATION
    elif unit in [member.value for member in UnitOfTemperature]:
        return  SensorDeviceClass.TEMPERATURE
    elif unit in [member.value for member in UnitOfVolume]:
        return SensorDeviceClass.VOLUME_STORAGE # Perhaps change this to water if only water is measured in volume units
    elif unit in [member.value for member in UnitOfSpeed]:
        if "meteo" in name:
            return SensorDeviceClass.WIND_SPEED
        return SensorDeviceClass.SPEED
    elif unit in [member.value for member in UnitOfPressure]:
        return SensorDeviceClass.PRESSURE
    elif unit == ELECTRIC_POTENTIAL_VOLT:
        return SensorDeviceClass.VOLTAGE
    elif unit == ELECTRIC_CURRENT_AMPERE:
        return SensorDeviceClass.CURRENT
    return None


@dataclass
class VictronEntityDescription(SensorEntityDescription, VictronBaseEntityDescription):
    """Describes victron sensor entity."""
    entity_type: ReadEntityType = None

class VictronSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Victron energy sensor."""

    def __init__(self, coordinator: victronEnergyDeviceUpdateCoordinator, description: VictronEntityDescription) -> None:
        """Initialize the sensor."""
        self.description: VictronEntityDescription = description
        self._attr_device_class = description.device_class
        self._attr_name = f"{description.name}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_state_class = description.state_class
        self.entity_type = description.entity_type

        #VE.CAN device zero is present under unit 100. This seperates non system / settings entities into the seperate can device
        if description.slave == 100 and not description.key.startswith(("settings", "system")) :
            actual_id = 0
        else:
            actual_id = description.slave

        self._attr_unique_id = f"{actual_id}_{self.description.key}"
        if actual_id not in (100, 225):
            self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}_{actual_id}"
        else:
            self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}"



        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""      
        try:
            data = self.description.value_fn(self.coordinator.processed_data(), self.description.slave, self.description.key)
            if self.entity_type is not None and isinstance(self.entity_type, TextReadEntityType):
                self._attr_native_value = self.entity_type.decodeEnum(data).name.split("_DUPLICATE")[0]
            else:
                self._attr_native_value = data
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
    def available(self) -> bool:
        full_key = str(self.description.slave) + "." + self.description.key
        return self.coordinator.processed_data()["availability"][full_key]

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return the device info."""
        return entity.DeviceInfo(
            identifiers={
                (DOMAIN, self.unique_id.split('_')[0])
            },
            name=self.unique_id.split('_')[1],
            model=self.unique_id.split('_')[0],
            manufacturer="victron", # to be dynamically set for gavazzi and redflow
        )