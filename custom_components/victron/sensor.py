"""Support for Victron energy sensors."""

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HassJob, HomeAssistant, callback
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .base import VictronBaseEntityDescription
from .const import (
    CONF_ADVANCED_OPTIONS,
    DOMAIN,
    BoolReadEntityType,
    ReadEntityType,
    TextReadEntityType,
    register_info_dict,
)
from .coordinator import victronEnergyDeviceUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victron energy sensor entries."""
    _LOGGER.debug("attempting to setup sensor entities")
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
                if config_entry.options[CONF_ADVANCED_OPTIONS]:
                    if not isinstance(
                        registerInfo.entityType, ReadEntityType
                    ) or isinstance(registerInfo.entityType, BoolReadEntityType):
                        continue

                description = VictronEntityDescription(
                    key=register_name,
                    name=register_name.replace("_", " "),
                    native_unit_of_measurement=registerInfo.unit,
                    state_class=registerInfo.determine_stateclass(),
                    slave=slave,
                    device_class=determine_victron_device_class(
                        register_name, registerInfo.unit
                    ),
                    entity_type=registerInfo.entityType
                    if isinstance(registerInfo.entityType, TextReadEntityType)
                    else None,
                )
                _LOGGER.debug("composed description == %s", description)

                descriptions.append(description)

    entities = []
    entity = {}
    for description in descriptions:
        entity = description
        entities.append(VictronSensor(victron_coordinator, entity))

    # Add an entity for each sensor type
    async_add_entities(entities, True)


def determine_victron_device_class(name, unit):
    """Determine the device class of a sensor based on its name and unit."""
    if unit == PERCENTAGE and "soc" in name:
        return SensorDeviceClass.BATTERY
    if unit == PERCENTAGE:
        return None  # Device classes aren't supported for voltage deviation and other % based entities that do not report SOC, moisture or humidity
    if unit in [member.value for member in UnitOfPower]:
        return SensorDeviceClass.POWER
    if unit in [member.value for member in UnitOfEnergy]:
        _LOGGER.debug("unit of energy")
        return SensorDeviceClass.ENERGY
    if unit == UnitOfFrequency.HERTZ:
        return SensorDeviceClass.FREQUENCY
    if unit == UnitOfTime.SECONDS:
        return SensorDeviceClass.DURATION
    if unit in [member.value for member in UnitOfTemperature]:
        return SensorDeviceClass.TEMPERATURE
    if unit in [member.value for member in UnitOfVolume]:
        return (
            SensorDeviceClass.VOLUME_STORAGE
        )  # Perhaps change this to water if only water is measured in volume units
    if unit in [member.value for member in UnitOfSpeed]:
        if "meteo" in name:
            return SensorDeviceClass.WIND_SPEED
        return SensorDeviceClass.SPEED
    if unit in [member.value for member in UnitOfPressure]:
        return SensorDeviceClass.PRESSURE
    if unit == UnitOfElectricPotential.VOLT:
        return SensorDeviceClass.VOLTAGE
    if unit == UnitOfElectricCurrent.AMPERE:
        return SensorDeviceClass.CURRENT
    return None


@dataclass
class VictronEntityDescription(SensorEntityDescription, VictronBaseEntityDescription):
    """Describes victron sensor entity."""

    entity_type: ReadEntityType = None


class VictronSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Victron energy sensor."""

    def __init__(
        self,
        coordinator: victronEnergyDeviceUpdateCoordinator,
        description: VictronEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.description: VictronEntityDescription = description
        self._attr_device_class = description.device_class
        self._attr_name = f"{description.name}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_state_class = description.state_class
        self.entity_type = description.entity_type

        self._attr_unique_id = f"{description.slave}_{self.description.key}"
        if description.slave not in (0, 100, 225):
            self.entity_id = (
                f"{SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}_{description.slave}"
            )
        else:
            self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{self.description.key}"

        self._update_job = HassJob(self.async_schedule_update_ha_state)
        self._unsub_update = None

        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Get the latest data and updates the states."""
        try:
            if self.available:
                data = self.description.value_fn(
                    self.coordinator.processed_data(),
                    self.description.slave,
                    self.description.key,
                )
                if self.entity_type is not None and isinstance(
                    self.entity_type, TextReadEntityType
                ):
                    if data in {item.value for item in self.entity_type.decodeEnum}:
                        self._attr_native_value = self.entity_type.decodeEnum(
                            data
                        ).name.split("_DUPLICATE")[0]
                    else:
                        self._attr_native_value = "NONDECODABLE"
                        _LOGGER.error(
                            "The reported value %s for entity %s isn't a decobale value. Please report this error to the integrations maintainer",
                            data,
                            self._attr_name,
                        )
                else:
                    self._attr_native_value = data

            self.async_write_ha_state()
        except (TypeError, IndexError):
            _LOGGER.debug("failed to retrieve value")
            # No data available
            self._attr_native_value = None

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
            manufacturer="victron",  # to be dynamically set for gavazzi and redflow
        )
