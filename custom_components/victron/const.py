"""Constants for the victron integration."""

from enum import Enum

from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfIrradiance,
    UnitOfLength,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)


class DeviceType(Enum):
    """Enum for device types."""

    grid = 1
    tank = 2
    multi = 3
    vebus = 4


DOMAIN = "victron"

CONF_HOST = "host"
CONF_PORT = "port"
SCAN_REGISTERS = "registers"
CONF_INTERVAL = "interval"
CONF_ADVANCED_OPTIONS = "advanced"
CONF_AC_CURRENT_LIMIT = "ac_current"
CONF_DC_CURRENT_LIMIT = "dc_current"
CONF_DC_SYSTEM_VOLTAGE = "dc_voltage"
CONF_AC_SYSTEM_VOLTAGE = "ac_voltage"
CONF_NUMBER_OF_PHASES = "number_of_phases"
CONF_USE_SLIDERS = "use_sliders"

AC_VOLTAGES = {
    "US (120)": 120,
    "EU (230)": 230,
}  # For now only most common voltages supported
DC_VOLTAGES = {
    "lifepo4_12v": 12,
    "lifepo4_24v": 24,
    "lifepo4_48v": 48,
}  # only 3 volt nominal 4s, 8s and 16s lifepo4 configurations currently supported
PHASE_CONFIGURATIONS = {"single phase": 1, "split phase": 2, "three phase": 3}


class STRING:
    """Class for string data type."""

    def __init__(self, length=1, read_length=None):
        """Initialize the string data type."""
        self.length = length
        self.readLength = read_length if read_length is not None else length * 2


# maybe change to enum Enum('UINT16', 'UINT32')
UINT16 = "uint16"
INT16 = "int16"
UINT32 = "uint32"
INT32 = "int32"

UINT16_MAX = 65535

TRANSLATED_ENTITY_TYPES = (
    "grid",
    "vebus",
    "battery",
    "pvinverter",
    "settings",
    "system",
)


class EntityType:
    """Base entityType."""

    def __init__(self, entityTypeName) -> None:
        """Initialize the entity type."""
        self.entityTypeName = entityTypeName


class ReadEntityType(EntityType):
    """Read entity type."""

    def __init__(self, entityTypeName: str = "read") -> None:
        """Initialize the read entity type."""
        super().__init__(entityTypeName=entityTypeName)


class TextReadEntityType(ReadEntityType):
    """Text read entity type."""

    def __init__(self, decodeEnum: Enum) -> None:
        """Initialize the text read entity type."""
        super().__init__()
        self.decodeEnum = decodeEnum


class BoolReadEntityType(ReadEntityType):
    """Bool read entity type."""

    def __init__(self) -> None:
        """Initialize the bool read entity type."""
        super().__init__(entityTypeName="bool")


class ButtonWriteType(EntityType):
    """Button write type."""

    def __init__(self) -> None:
        """Initialize the button write type."""
        super().__init__(entityTypeName="button")


class SwitchWriteType(EntityType):
    """Switch write type."""

    def __init__(self) -> None:
        """Initialize the switch write type."""
        super().__init__(entityTypeName="switch")


class SliderWriteType(EntityType):
    """Slider write type."""

    def __init__(self, powerType="", negative: bool = False) -> None:
        """Initialize the slider write type."""
        super().__init__(entityTypeName="slider")
        self.powerType = powerType
        self.negative = negative


class SelectWriteType(EntityType):
    """Select write type."""

    def __init__(self, optionsEnum: Enum) -> None:
        """Initialize the select write type."""
        super().__init__(entityTypeName="select")
        self.options = optionsEnum


class RegisterInfo:
    """Class for register information."""

    def __init__(
        self,
        register,
        dataType,
        unit="",
        scale=1,
        entityType: EntityType = ReadEntityType(),
        step=0,
    ) -> None:
        """Initialize the register info."""
        self.register = register
        self.dataType = dataType
        self.unit = (
            unit
            if not isinstance(entityType, TextReadEntityType)
            and not isinstance(dataType, STRING)
            else None
        )
        self.scale = scale
        self.step = step
        # Only used for writeable entities
        self.entityType = entityType

    def determine_stateclass(self):
        """Determine the state class."""
        if self.unit == UnitOfEnergy.KILO_WATT_HOUR:
            return SensorStateClass.TOTAL_INCREASING
        if self.unit is None:
            return None
        return SensorStateClass.MEASUREMENT


class generic_alarm_ledger(Enum):
    """Generic alarm ledger."""

    ok = 0
    warning = 1
    alarm = 2


gavazi_grid_registers = {
    "grid_L1_power": RegisterInfo(2600, INT16, UnitOfPower.WATT),
    "grid_L2_power": RegisterInfo(2601, INT16, UnitOfPower.WATT),
    "grid_L3_power": RegisterInfo(2602, INT16, UnitOfPower.WATT),
    "grid_L1_energy_forward": RegisterInfo(
        2603, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L3_energy_forward": RegisterInfo(
        2605, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L2_energy_forward": RegisterInfo(
        2604, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L1_energy_reverse": RegisterInfo(
        2606, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L2_energy_reverse": RegisterInfo(
        2607, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L3_energy_reverse": RegisterInfo(
        2608, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_serial": RegisterInfo(2609, STRING(7)),
    "grid_L1_voltage": RegisterInfo(2616, UINT16, UnitOfElectricPotential.VOLT, 10),
    "grid_L1_current": RegisterInfo(2617, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "grid_L2_voltage": RegisterInfo(2618, UINT16, UnitOfElectricPotential.VOLT, 10),
    "grid_L2_current": RegisterInfo(2619, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "grid_L3_voltage": RegisterInfo(2620, UINT16, UnitOfElectricPotential.VOLT, 10),
    "grid_L3_current": RegisterInfo(2621, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "grid_L1_energy_forward_total": RegisterInfo(
        2622, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L2_energy_forward_total": RegisterInfo(
        2624, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L3_energy_forward_total": RegisterInfo(
        2626, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L1_energy_reverse_total": RegisterInfo(
        2628, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L2_energy_reverse_total": RegisterInfo(
        2630, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_L3_energy_reverse_total": RegisterInfo(
        2632, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_energy_forward_total": RegisterInfo(
        2634, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "grid_energy_reverse_total": RegisterInfo(
        2636, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
}


class vebus_mode(Enum):
    """Vebus mode."""

    charger = 1
    inverter = 2
    on = 3
    off = 4


class generic_activeinput(Enum):
    """Generic active input."""

    ac_input_1 = 0
    ac_input_2 = 1
    disconnected = 240


class generic_charger_state(Enum):
    """Generic charger state."""

    off = 0
    low_power = 1
    fault = 2
    bulk = 3
    absorption = 4
    float = 5
    storage = 6
    equalize = 7
    passthru = 8
    inverting = 9
    power_assist = 10
    power_supply = 11
    external_control = 252


class vebus_error(Enum):
    """Vebus error."""

    ok = 0
    external_phase_triggered_switchoff = 1
    mk2_type_mismatch = 2
    device_count_mismatch = 3
    no_other_devices = 4
    ac_overvoltage_out = 5
    ddc_program = 6
    bms_without_assistant_connected = 7
    time_sync_mismatch = 10
    cannot_transmit = 14
    dongle_absent = 16
    master_failover = 17
    ac_overvoltage_slave_off = 18
    cannot_be_slave = 22
    switch_over_protection = 24
    firmware_incompatibiltiy = 25
    internal_error = 26


vebus_registers = {
    "vebus_activein_L1_voltage": RegisterInfo(
        3, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "vebus_activein_L2_voltage": RegisterInfo(
        4, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "vebus_activein_L3_voltage": RegisterInfo(
        5, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "vebus_activein_L1_current": RegisterInfo(
        6, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "vebus_activein_L2_current": RegisterInfo(
        7, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "vebus_activein_L3_current": RegisterInfo(
        8, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "vebus_activein_L1_frequency": RegisterInfo(9, INT16, UnitOfFrequency.HERTZ, 100),
    "vebus_activein_L2_frequency": RegisterInfo(10, INT16, UnitOfFrequency.HERTZ, 100),
    "vebus_activein_L3_frequency": RegisterInfo(11, INT16, UnitOfFrequency.HERTZ, 100),
    "vebus_activein_L1_power": RegisterInfo(
        12, INT16, UnitOfPower.WATT, 0.1
    ),  # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_activein_L2_power": RegisterInfo(
        13, INT16, UnitOfPower.WATT, 0.1
    ),  # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_activein_L3_power": RegisterInfo(
        14, INT16, UnitOfPower.WATT, 0.1
    ),  # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_out_L1_voltage": RegisterInfo(15, UINT16, UnitOfElectricPotential.VOLT, 10),
    "vebus_out_L2_voltage": RegisterInfo(16, UINT16, UnitOfElectricPotential.VOLT, 10),
    "vebus_out_L3_voltage": RegisterInfo(17, UINT16, UnitOfElectricPotential.VOLT, 10),
    "vebus_out_L1_current": RegisterInfo(18, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "vebus_out_L2_current": RegisterInfo(19, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "vebus_out_L3_current": RegisterInfo(20, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "vebus_out_L1_frequency": RegisterInfo(21, INT16, UnitOfFrequency.HERTZ, 100),
    "vebus_activein_currentlimit": RegisterInfo(
        22, INT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", True)
    ),
    "vebus_out_L1_power": RegisterInfo(23, INT16, UnitOfPower.WATT, 0.1),
    "vebus_out_L2_power": RegisterInfo(24, INT16, UnitOfPower.WATT, 0.1),
    "vebus_out_L3_power": RegisterInfo(25, INT16, UnitOfPower.WATT, 0.1),
    "vebus_battery_voltage": RegisterInfo(
        26, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "vebus_battery_current": RegisterInfo(27, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "vebus_numberofphases": RegisterInfo(
        28, UINT16
    ),  # the number count has no unit of measurement
    "vebus_activein_activeinput": RegisterInfo(
        register=29, dataType=UINT16, entityType=TextReadEntityType(generic_activeinput)
    ),
    "vebus_soc": RegisterInfo(
        30, UINT16, PERCENTAGE, 10, SliderWriteType(PERCENTAGE, False)
    ),
    "vebus_state": RegisterInfo(
        register=31,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_state),
    ),  # This has no unit of measurement
    "vebus_error": RegisterInfo(
        register=32, dataType=UINT16, entityType=TextReadEntityType(vebus_error)
    ),  # This has no unit of measurement
    "vebus_mode": RegisterInfo(
        register=33, dataType=UINT16, entityType=SelectWriteType(vebus_mode)
    ),  # This has no unit of measurement
    "vebus_alarm_hightemperature": RegisterInfo(
        register=34,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_lowbattery": RegisterInfo(
        register=35,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_overload": RegisterInfo(
        register=36,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_L1_acpowersetpoint": RegisterInfo(
        register=37,
        dataType=INT16,
        unit=UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "vebus_disablecharge": RegisterInfo(
        register=38, dataType=UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_disablefeedin": RegisterInfo(
        39, UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_L2_acpowersetpoint": RegisterInfo(
        register=40,
        dataType=INT16,
        unit=UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "vebus_L3_acpowersetpoint": RegisterInfo(
        register=41,
        dataType=INT16,
        unit=UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "vebus_alarm_temperaturesensor": RegisterInfo(
        register=42,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_voltagesensor": RegisterInfo(
        register=43,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L1_higtemperature": RegisterInfo(
        register=44,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L1_lowbattery": RegisterInfo(
        register=45,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L1_overload": RegisterInfo(
        register=46,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L1_ripple": RegisterInfo(
        register=47,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L2_higtemperature": RegisterInfo(
        register=48,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L2_lowbattery": RegisterInfo(
        register=49,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L2_overload": RegisterInfo(
        register=50,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L2_ripple": RegisterInfo(
        register=51,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L3_higtemperature": RegisterInfo(
        register=52,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L3_lowbattery": RegisterInfo(
        register=53,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L3_overload": RegisterInfo(
        register=54,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_L3_ripple": RegisterInfo(
        register=55,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_pvinverter_disable": RegisterInfo(
        register=56, dataType=UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_bms_allowtocharge": RegisterInfo(
        register=57, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_bms_allowtodischarge": RegisterInfo(
        register=58, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_bms_bmsexpected": RegisterInfo(
        register=59, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_bms_error": RegisterInfo(
        register=60, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_battery_temperature": RegisterInfo(61, INT16, UnitOfTemperature.CELSIUS, 10),
    "vebus_systemreset": RegisterInfo(
        register=62, dataType=UINT16, entityType=ButtonWriteType()
    ),  # This has no unit of measurement
    "vebus_alarm_phaserotation": RegisterInfo(
        register=63,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_alarm_gridlost": RegisterInfo(
        register=64,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),  # This has no unit of measurement
    "vebus_donotfeedinovervoltage": RegisterInfo(
        register=65, dataType=UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_L1_maxfeedinpower": RegisterInfo(
        66, UINT16, UnitOfPower.WATT, 0.01, SliderWriteType("AC", False)
    ),
    "vebus_L2_maxfeedinpower": RegisterInfo(
        67, UINT16, UnitOfPower.WATT, 0.01, SliderWriteType("AC", False)
    ),
    "vebus_L3_maxfeedinpower": RegisterInfo(
        68, UINT16, UnitOfPower.WATT, 0.01, SliderWriteType("AC", False)
    ),
    "vebus_state_ignoreacin1": RegisterInfo(
        register=69, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_state_ignoreacin2": RegisterInfo(
        register=70, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_targetpowerismaxfeedin": RegisterInfo(
        register=71, dataType=UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_fixsolaroffsetto100mv": RegisterInfo(
        register=72, dataType=UINT16, entityType=SwitchWriteType()
    ),  # This has no unit of measurement
    "vebus_sustain": RegisterInfo(
        register=73, dataType=UINT16, entityType=BoolReadEntityType()
    ),  # This has no unit of measurement
    "vebus_acin1toacout": RegisterInfo(74, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin1toinverter": RegisterInfo(76, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin2toacout": RegisterInfo(78, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin2toinverter": RegisterInfo(80, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acouttoacin1": RegisterInfo(82, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acouttoacin2": RegisterInfo(84, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacin1": RegisterInfo(86, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacin2": RegisterInfo(88, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacout": RegisterInfo(90, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_outtoinverter": RegisterInfo(92, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
}

battery_registers = {
    "battery_voltage": RegisterInfo(259, UINT16, UnitOfElectricPotential.VOLT, 100),
    "battery_starter_voltage": RegisterInfo(
        260, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_current": RegisterInfo(261, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "battery_temperature": RegisterInfo(262, INT16, UnitOfTemperature.CELSIUS, 10),
    "battery_midvoltage": RegisterInfo(263, UINT16, UnitOfElectricPotential.VOLT, 100),
    "battery_midvoltagedeviation": RegisterInfo(264, UINT16, PERCENTAGE, 100),
    "battery_consumedamphours": RegisterInfo(
        265, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),
    "battery_soc": RegisterInfo(266, UINT16, PERCENTAGE, 10),
    "battery_alarm": RegisterInfo(
        register=267,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowvoltage": RegisterInfo(
        register=268,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highvoltage": RegisterInfo(
        register=269,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowstartervoltage": RegisterInfo(
        register=270,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highstartervoltage": RegisterInfo(
        register=271,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowsoc": RegisterInfo(
        register=272,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowtemperature": RegisterInfo(
        register=273,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_hightemperature": RegisterInfo(
        register=274,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_midvoltage": RegisterInfo(
        register=275,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowfusedvoltage": RegisterInfo(
        register=276,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highfusedvoltage": RegisterInfo(
        register=277,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_fuseblown": RegisterInfo(
        register=278,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highinternaltemperature": RegisterInfo(
        register=279,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_relay": RegisterInfo(
        register=280, dataType=UINT16, entityType=SwitchWriteType()
    ),
    "battery_history_deepestdischarge": RegisterInfo(
        281, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),
    "battery_history_lastdischarge": RegisterInfo(
        282, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),
    "battery_history_averagedischarge": RegisterInfo(
        283, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),
    "battery_history_chargecycles": RegisterInfo(284, UINT16),
    "battery_history_fulldischarges": RegisterInfo(285, UINT16),
    "battery_history_totalahdrawn": RegisterInfo(
        286, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),
    "battery_history_minimumvoltage": RegisterInfo(
        287, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_maximumvoltage": RegisterInfo(
        288, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_timesincelastfullcharge": RegisterInfo(
        289, UINT16, UnitOfTime.SECONDS, 0.01
    ),
    "battery_history_automaticsyncs": RegisterInfo(290, UINT16),
    "battery_history_lowvoltagealarms": RegisterInfo(291, UINT16),
    "battery_history_highvoltagealarms": RegisterInfo(292, UINT16),
    "battery_history_lowstartervoltagealarms": RegisterInfo(293, UINT16),
    "battery_history_highstartervoltagealarms": RegisterInfo(294, UINT16),
    "battery_history_minimumstartervoltage": RegisterInfo(
        295, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_maximumstartervoltage": RegisterInfo(
        296, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_lowfusedvoltagealarms": RegisterInfo(297, UINT16),
    "battery_history_highfusedvoltagealarms": RegisterInfo(298, UINT16),
    "battery_history_minimumfusedvoltage": RegisterInfo(
        299, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_maximumfusedvoltage": RegisterInfo(
        300, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_dischargedenergy": RegisterInfo(
        301, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "battery_history_chargedenergy": RegisterInfo(
        302, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "battery_timetogo": RegisterInfo(303, UINT16, UnitOfTime.SECONDS, 0.01),
    "battery_soh": RegisterInfo(304, UINT16, PERCENTAGE, 10),
    "battery_info_maxchargevoltage": RegisterInfo(
        305, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "battery_info_batterylowvoltage": RegisterInfo(
        306, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "battery_info_maxchargecurrent": RegisterInfo(
        307, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "battery_info_maxdischargecurrent": RegisterInfo(
        308, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "battery_capacity": RegisterInfo(309, UINT16, UnitOfElectricCurrent.AMPERE, 10),
    "battery_diagnostics_lasterror_1_time": RegisterInfo(310, INT32, "timestamp"),
    "battery_diagnostics_lasterror_2_time": RegisterInfo(312, INT32, "timestamp"),
    "battery_diagnostics_lasterror_3_time": RegisterInfo(314, INT32, "timestamp"),
    "battery_diagnostics_lasterror_4_time": RegisterInfo(316, INT32, "timestamp"),
    "battery_system_mincelltemperature": RegisterInfo(
        318, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "battery_system_maxcelltemperature": RegisterInfo(
        319, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "battery_alarm_higchargecurrent": RegisterInfo(
        register=320,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highdischargecurrent": RegisterInfo(
        register=321,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_cellimbalance": RegisterInfo(
        register=322,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_internalfailure": RegisterInfo(
        register=323,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_highchargetemperature": RegisterInfo(
        register=324,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowchargetemperature": RegisterInfo(
        register=325,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "battery_alarm_lowcellvoltage": RegisterInfo(
        register=326,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class battery_state(Enum):
    """Battery state."""

    wait_start_init = 0
    before_boot_init = 1
    before_boot_delay_init = 2
    wait_boot_init = 3
    initializing = 4
    battery_voltage_measure_init = 5
    battery_calculate_voltage_init = 6
    wait_bus_voltage_init = 7
    wait_lynx_shunt_init = 8
    running = 9
    error = 10
    unused = 11
    shutdown = 12
    slave_updating = 13
    standby = 14
    going_to_run = 15
    pre_charging = 16


class battery_error(Enum):
    """Battery error."""

    none = 0
    battery_init_error = 1
    no_batteries_connected = 2
    unknown_battery_connected = 3
    different_battery_type = 4
    number_of_batteries_incorrect = 5
    lynx_shunt_not_found = 6
    battery_measure_error = 7
    internal_calculation_error = 8
    batteries_in_series_not_ok = 9
    number_of_batteries_incorrect_duplicate_1 = 10
    hardware_error = 11
    watchdog_error = 12
    over_voltage = 13
    under_voltage = 14
    over_temperature = 15
    under_temperature = 16
    hardware_fault = 17
    standby_shutdown = 18
    pre_charge_charge_error = 19
    safety_contactor_check_error = 20
    pre_charge_discharge_error = 21
    adc_error = 22
    slave_error = 23
    slave_warning = 24
    pre_charge_error = 25
    safety_contactor_error = 26
    over_current = 27
    slave_update_failed = 28
    slave_update_unavailable = 29
    calibration_data_lost = 30
    settings_invalid = 31
    bms_cable = 32
    reference_failure = 33
    wrong_system_voltage = 34
    pre_charge_timeout = 35


battery_detail_registers = {
    "battery_state": RegisterInfo(
        register=1282, dataType=UINT16, entityType=TextReadEntityType(battery_state)
    ),
    "battery_error": RegisterInfo(
        register=1283, dataType=UINT16, entityType=TextReadEntityType(battery_error)
    ),
    "battery_system_switch": RegisterInfo(
        register=1284, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "battery_balancing": RegisterInfo(
        register=1285, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "battery_system_numberofbatteries": RegisterInfo(1286, UINT16),
    "battery_system_batteriesparallel": RegisterInfo(1287, UINT16),
    "battery_system_batteriesseries": RegisterInfo(1288, UINT16),
    "battery_system_numberofcellsperbattery": RegisterInfo(1289, UINT16),
    "battery_system_mincellvoltage": RegisterInfo(
        1290, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_system_maxcellvoltage": RegisterInfo(
        1291, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_diagnostics_shutdownsdueerror": RegisterInfo(1292, UINT16),
    "battery_diagnostics_lasterror_1": RegisterInfo(
        register=1293, dataType=UINT16, entityType=TextReadEntityType(battery_error)
    ),
    "battery_diagnostics_lasterror_2": RegisterInfo(
        register=1294, dataType=UINT16, entityType=TextReadEntityType(battery_error)
    ),
    "battery_diagnostics_lasterror_3": RegisterInfo(
        register=1295, dataType=UINT16, entityType=TextReadEntityType(battery_error)
    ),
    "battery_diagnostics_lasterror_4": RegisterInfo(
        register=1296, dataType=UINT16, entityType=TextReadEntityType(battery_error)
    ),
    "battery_io_allowtocharge": RegisterInfo(
        register=1297, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "battery_io_allowtodischarge": RegisterInfo(
        register=1298, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "battery_io_externalrelay": RegisterInfo(
        register=1299, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "battery_history_minimumcellvoltage": RegisterInfo(
        1300, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_history_maximumcellvoltage": RegisterInfo(
        1301, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_system_numberofmodulesoffline": RegisterInfo(1302, UINT16),
    "battery_system_numberofmodulesonline": RegisterInfo(1303, UINT16),
    "battery_system_numberofmodulesblockingcharge": RegisterInfo(1304, UINT16),
    "battery_system_numberofmodulesblockingdischarge": RegisterInfo(1305, UINT16),
    "battery_system_minvoltagecellid": RegisterInfo(1306, STRING(4)),
    "battery_system_maxvoltagecellid": RegisterInfo(1310, STRING(4)),
    "battery_system_mintemperaturecellid": RegisterInfo(1314, STRING(4)),
    "battery_system_maxtemperaturecellid": RegisterInfo(1318, STRING(4)),
}


class solarcharger_mode(Enum):
    """Solar charger mode."""

    on = 1
    off = 4


class solarcharger_state(Enum):
    """Solar charger state."""

    off = 0
    fault = 2
    bulk = 3
    absorption = 4
    float = 5
    storage = 6
    equalize = 7
    other_hub_1 = 11
    wake_up = 245
    external_control = 252


class solarcharger_equalization_pending(Enum):
    """Solar charger equalization pending."""

    no = 0
    yes = 1
    error = 2
    unavailable = 3


class generic_charger_errorcode(Enum):
    """Generic charger error code."""

    none = 0
    temperature_high = 1
    voltage_high = 2
    temperature_sensor_plus_miswired = 3
    temperature_sensor_min_miswired = 4
    temperature_sensor_disconnected = 5
    voltage_sense_plus_miswired = 6
    voltage_sense_min_miswired = 7
    voltage_sense_disconnected = 8
    voltage_wire_losses_too_high = 9
    charger_temperature_too_high = 17
    charger_over_current = 18
    charger_polarity_reversed = 19
    bulk_time_limit = 20
    charger_temperature_sensor_miswired = 22
    charger_temperature_sensor_disconnected = 23
    input_current_too_high = 34


class generic_mppoperationmode(Enum):
    """Generic MPP operation mode."""

    off = 0
    limited = 1
    active = 2
    unavailable = 255


solarcharger_registers = {
    "solarcharger_battery_voltage": RegisterInfo(
        771, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "solarcharger_battery_current": RegisterInfo(
        772, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "solarcharger_battery_temperature": RegisterInfo(
        773, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "solarcharger_mode": RegisterInfo(
        register=774, dataType=UINT16, entityType=SelectWriteType(solarcharger_mode)
    ),
    "solarcharger_state": RegisterInfo(
        register=775, dataType=UINT16, entityType=TextReadEntityType(solarcharger_state)
    ),
    "solarcharger_pv_voltage": RegisterInfo(
        776, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "solarcharger_pv_current": RegisterInfo(
        777, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "solarcharger_equallization_pending": RegisterInfo(
        register=778,
        dataType=UINT16,
        entityType=TextReadEntityType(solarcharger_equalization_pending),
    ),
    "solarcharger_equalization_time_remaining": RegisterInfo(
        779, UINT16, UnitOfTime.SECONDS, 10
    ),
    "solarcharger_relay": RegisterInfo(
        register=780, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "solarcharger_alarm": RegisterInfo(
        register=781,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "solarcharger_alarm_lowvoltage": RegisterInfo(
        register=782,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "solarcharger_alarm_highvoltage": RegisterInfo(
        register=783,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "solarcharger_yield_today": RegisterInfo(
        784, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_maxpower_today": RegisterInfo(785, UINT16, UnitOfPower.WATT),
    "solarcharger_yield_yesterday": RegisterInfo(
        786, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_maxpower_yesterday": RegisterInfo(787, UINT16, UnitOfPower.WATT),
    "solarcharger_errorcode": RegisterInfo(
        register=788,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_errorcode),
    ),
    "solarcharger_yield_power": RegisterInfo(789, UINT16, UnitOfPower.WATT, 10),
    "solarcharger_yield_user": RegisterInfo(
        790, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_mppoperationmode": RegisterInfo(
        register=791,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_mppoperationmode),
    ),
}

solarcharger_tracker_voltage_registers = {
    "solarcharger_tracker_0_voltage": RegisterInfo(
        3700, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "solarcharger_tracker_1_voltage": RegisterInfo(
        3701, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "solarcharger_tracker_2_voltage": RegisterInfo(
        3702, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "solarcharger_tracker_3_voltage": RegisterInfo(
        3703, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
}

solarcharger_tracker_registers = {
    "solarcharger_tracker_0_yield_today": RegisterInfo(
        3708, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_1_yield_today": RegisterInfo(
        3709, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_2_yield_today": RegisterInfo(
        3710, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_3_yield_today": RegisterInfo(
        3711, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_0_yield_yesterday": RegisterInfo(
        3712, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_1_yield_yesterday": RegisterInfo(
        3713, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_2_yield_yesterday": RegisterInfo(
        3714, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_3_yield_yesterday": RegisterInfo(
        3715, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "solarcharger_tracker_0_maxpower_today": RegisterInfo(
        3716, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_1_maxpower_today": RegisterInfo(
        3717, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_2_maxpower_today": RegisterInfo(
        3718, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_3_maxpower_today": RegisterInfo(
        3719, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_0_maxpower_yesterday": RegisterInfo(
        3720, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_1_maxpower_yesterday": RegisterInfo(
        3721, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_2_maxpower_yesterday": RegisterInfo(
        3722, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_3_maxpower_yesterday": RegisterInfo(
        3723, UINT16, UnitOfPower.WATT
    ),
    "solarcharger_tracker_0_pv_power": RegisterInfo(3724, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_1_pv_power": RegisterInfo(3725, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_2_pv_power": RegisterInfo(3726, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_3_pv_power": RegisterInfo(3727, UINT16, UnitOfPower.WATT),
}


class generic_position(Enum):
    """Generic position."""

    ac_input_1 = 0
    ac_output = 1
    ac_input_2 = 2


pvinverter_registers = {
    "pvinverter_position": RegisterInfo(
        register=1026, dataType=UINT16, entityType=TextReadEntityType(generic_position)
    ),
    "pvinverter_L1_voltage": RegisterInfo(
        1027, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "pvinverter_L1_current": RegisterInfo(
        1028, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "pvinverter_L1_power": RegisterInfo(1029, UINT16, UnitOfPower.WATT),
    "pvinverter_L1_energy_forward": RegisterInfo(
        1030, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_L2_voltage": RegisterInfo(
        1031, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "pvinverter_L2_current": RegisterInfo(
        1032, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "pvinverter_L2_power": RegisterInfo(1033, UINT16, UnitOfPower.WATT),
    "pvinverter_L2_energy_forward": RegisterInfo(
        1034, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_L3_voltage": RegisterInfo(
        1035, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "pvinverter_L3_current": RegisterInfo(
        1036, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "pvinverter_L3_power": RegisterInfo(1037, UINT16, UnitOfPower.WATT),
    "pvinverter_L3_energy_forward": RegisterInfo(
        1038, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_serial": RegisterInfo(1039, STRING(7)),
    "pvinverter_L1_energy_forward_total": RegisterInfo(
        1046, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_L2_energy_forward_total": RegisterInfo(
        1048, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_L3_energy_forward_total": RegisterInfo(
        1050, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "pvinverter_power_total": RegisterInfo(1052, INT32, UnitOfPower.WATT),
    "pvinverter_power_max_capacity": RegisterInfo(1054, UINT32, UnitOfPower.WATT),
    "pvinverter_powerlimit": RegisterInfo(
        register=1056,
        dataType=UINT32,
        unit=UnitOfPower.WATT,
        entityType=SliderWriteType("AC", False),
    ),
}

motordrive_registers = {
    "motordrive_rpm": RegisterInfo(2048, INT16, REVOLUTIONS_PER_MINUTE),
    "motordrive_motor_temperature": RegisterInfo(
        2049, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "motordrive_voltage": RegisterInfo(2050, UINT16, UnitOfElectricPotential.VOLT, 100),
    "motordrive_current": RegisterInfo(2051, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "motordrive_power": RegisterInfo(2052, INT16, UnitOfPower.WATT, 10),
    "motordrive_controller_temperature": RegisterInfo(
        2053, INT16, UnitOfTemperature.CELSIUS, 10
    ),
}


class charger_mode(Enum):
    """Charger mode."""

    off = 0
    on = 1
    error = 2
    unavailable = 3


charger_registers = {
    "charger_voltage_output_1": RegisterInfo(
        2307, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "charger_current_output_1": RegisterInfo(
        2308, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "charger_temperature": RegisterInfo(2309, INT16, UnitOfTemperature.CELSIUS, 10),
    "charger_voltage_output_2": RegisterInfo(
        2310, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "charger_current_output_2": RegisterInfo(
        2311, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "charger_voltage_output_3": RegisterInfo(
        2312, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "charger_current_output_3": RegisterInfo(
        2313, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "charger_L1_current": RegisterInfo(2314, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "charger_L1_power": RegisterInfo(2315, UINT16, UnitOfPower.WATT),
    "charger_current_limit": RegisterInfo(
        2316,
        INT16,
        UnitOfElectricCurrent.AMPERE,
        10,
        entityType=SliderWriteType("AC", True),
    ),
    "charger_mode": RegisterInfo(
        register=2317, dataType=UINT16, entityType=SelectWriteType(charger_mode)
    ),
    "charger_state": RegisterInfo(
        register=2318,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_state),
    ),
    "charger_errorcode": RegisterInfo(
        register=2319,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_errorcode),
    ),
    "charger_relay": RegisterInfo(
        register=2320, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "charger_alarm_lowvoltage": RegisterInfo(
        register=2321,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "charger_alarm_highvoltage": RegisterInfo(
        register=2322,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}

settings_registers = {
    "settings_ess_acpowersetpoint": RegisterInfo(
        register=2700,
        dataType=INT16,
        unit=UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "settings_ess_maxchargepercentage": RegisterInfo(
        register=2701, dataType=UINT16, unit=PERCENTAGE, entityType=SliderWriteType()
    ),
    "settings_ess_maxdischargepercentage": RegisterInfo(
        register=2702, dataType=UINT16, unit=PERCENTAGE, entityType=SliderWriteType()
    ),
    "settings_ess_acpowersetpoint2": RegisterInfo(
        2703, INT16, UnitOfPower.WATT, 0.01, SliderWriteType("AC", True)
    ),  # NOTE: Duplicate register exposed by victron
    "settings_ess_maxdischargepower": RegisterInfo(
        2704, UINT16, UnitOfPower.WATT, 0.1, SliderWriteType("DC", False), 50
    ),
    "settings_ess_maxchargecurrent": RegisterInfo(
        register=2705,
        dataType=INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        entityType=SliderWriteType("DC", True),
    ),
    "settings_ess_maxfeedinpower": RegisterInfo(
        2706, INT16, UnitOfPower.WATT, 0.01, SliderWriteType("AC", True)
    ),
    "settings_ess_overvoltagefeedin": RegisterInfo(
        register=2707, dataType=INT16, entityType=SwitchWriteType()
    ),
    "settings_ess_preventfeedback": RegisterInfo(
        register=2708, dataType=INT16, entityType=SwitchWriteType()
    ),
    "settings_ess_feedinpowerlimit": RegisterInfo(
        register=2709, dataType=INT16, entityType=BoolReadEntityType()
    ),
    "settings_systemsetup_maxchargevoltage": RegisterInfo(
        2710,
        UINT16,
        UnitOfElectricPotential.VOLT,
        10,
        SliderWriteType("DC", False),
        0.1,
    ),
}

gps_registers = {
    "gps_latitude": RegisterInfo(2800, INT32, "", 10000000),
    "gps_longitude": RegisterInfo(2802, INT32, "", 10000000),
    "gps_course": RegisterInfo(2804, UINT16, "", 100),
    "gps_speed": RegisterInfo(2805, UINT16, UnitOfSpeed.METERS_PER_SECOND, 100),
    "gps_fix": RegisterInfo(
        register=2806, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "gps_numberofsatellites": RegisterInfo(2807, UINT16),
    "gps_altitude": RegisterInfo(2808, INT32, UnitOfLength.METERS, 10),
}


class ess_batterylife_state(Enum):
    """ESS battery life state."""

    bl_disabled_duplicate_1 = 0
    restarting = 1
    self_consumption = 2
    self_consumption_duplicate_1 = 3
    self_consumption_duplicate_2 = 4
    discharge_disabled = 5
    force_charge = 6
    sustain = 7
    low_soc_recharge = 8
    keep_batteries_charged = 9
    bl_disabled = 10
    bl_disabled_low_soc = 11
    bl_disabled_loc_soc_recharge = 12


class ess_mode(Enum):
    """ESS mode."""

    self_consumption_with_battery_life = 0
    self_consumption = 1
    keep_charged = 2
    external_control = 3


settings_ess_registers = {
    "settings_ess_batterylife_state": RegisterInfo(
        register=2900,
        dataType=UINT16,
        entityType=SelectWriteType(ess_batterylife_state),
    ),
    "settings_ess_batterylife_minimumsoc": RegisterInfo(
        2901, UINT16, PERCENTAGE, 10, SliderWriteType(), 5
    ),
    "settings_ess_mode": RegisterInfo(
        register=2902, dataType=UINT16, entityType=SelectWriteType(ess_mode)
    ),
    "settings_ess_batterylife_soclimit": RegisterInfo(2903, UINT16, PERCENTAGE, 10),
}


class tank_fluidtype(Enum):
    """Tank fluid type."""

    fuel = 0
    fresh_water = 1
    waste_water = 2
    live_well = 3
    oil = 4
    sewage_water = 5
    gasoline = 6
    diesel = 7
    lpg = 8
    lng = 9
    hydraulic_oil = 10
    raw_water = 11


class tank_status(Enum):
    """Tank status."""

    ok = 0
    disconnected = 1
    short_circuited = 2
    reverse_polarity = 3
    unknown = 4
    error = 5


tank_registers = {
    "tank_productid": RegisterInfo(3000, UINT16),
    "tank_capacity": RegisterInfo(3001, UINT32, UnitOfVolume.CUBIC_METERS, 10000),
    "tank_fluidtype": RegisterInfo(
        register=3003, dataType=UINT16, entityType=TextReadEntityType(tank_fluidtype)
    ),
    "tank_level": RegisterInfo(3004, UINT16, PERCENTAGE, 10),
    "tank_remaining": RegisterInfo(3005, UINT32, UnitOfVolume.CUBIC_METERS, 10000),
    "tank_status": RegisterInfo(
        register=3007, dataType=UINT16, entityType=TextReadEntityType(tank_status)
    ),
}

inverter_output_registers = {
    "inverter_output_L1_current": RegisterInfo(
        3100, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "inverter_output_L1_voltage": RegisterInfo(
        3101, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "inverter_output_L1_power": RegisterInfo(3102, INT16, UnitOfPower.WATT, 0.1),
}

inverter_battery_registers = {
    "inverter_battery_voltage": RegisterInfo(
        3105, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "inverter_battery_current": RegisterInfo(
        3106, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
}

inverter_alarm_registers = {
    "inverter_alarm_hightemperature": RegisterInfo(
        register=3110,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_highbatteryvoltage": RegisterInfo(
        register=3111,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_highacoutvoltage": RegisterInfo(
        register=3112,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_lowtemperature": RegisterInfo(
        register=3113,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_lowbatteryvoltage": RegisterInfo(
        register=3114,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_lowacoutvoltage": RegisterInfo(
        register=3115,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_overload": RegisterInfo(
        register=3116,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "inverter_alarm_ripple": RegisterInfo(
        register=3117,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class inverter_mode(Enum):
    """Inverter mode."""

    on = 2
    off = 4
    eco = 5


inverter_info_registers = {
    "inverter_info_firmwareversion": RegisterInfo(3125, UINT16),
    "inverter_info_mode": RegisterInfo(
        register=3126, dataType=UINT16, entityType=SelectWriteType(inverter_mode)
    ),
    "inverter_info_productid": RegisterInfo(3127, UINT16),
    "inverter_info_state": RegisterInfo(
        register=3128,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_state),
    ),
}

# PV voltage is present here due to poor register id selection by victron
inverter_energy_registers = {
    "inverter_energy_invertertoacout": RegisterInfo(
        3130, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "inverter_energy_outtoinverter": RegisterInfo(
        3132, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "inverter_energy_solartoacout": RegisterInfo(
        3134, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "inverter_energy_solartobattery": RegisterInfo(
        3136, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "inverter_pv_voltage_single_tracker": RegisterInfo(
        3138, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
}

inverter_tracker_registers = {
    "inverter_tracker_0_voltage": RegisterInfo(
        3140, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "inverter_tracker_1_voltage": RegisterInfo(
        3141, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "inverter_tracker_2_voltage": RegisterInfo(
        3142, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "inverter_tracker_3_voltage": RegisterInfo(
        3143, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
}

inverter_tracker_statistics_registers = {
    "inverter_tracker_0_yield_today": RegisterInfo(
        3148, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_1_yield_today": RegisterInfo(
        3149, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_2_yield_today": RegisterInfo(
        3150, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_3_yield_today": RegisterInfo(
        3151, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_0_yield_yesterday": RegisterInfo(
        3152, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_1_yield_yesterday": RegisterInfo(
        3153, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_2_yield_yesterday": RegisterInfo(
        3154, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_3_yield_yesterday": RegisterInfo(
        3155, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "inverter_tracker_0_maxpower_today": RegisterInfo(3156, UINT16, UnitOfPower.WATT),
    "inverter_tracker_1_maxpower_today": RegisterInfo(3157, UINT16, UnitOfPower.WATT),
    "inverter_tracker_2_maxpower_today": RegisterInfo(3158, UINT16, UnitOfPower.WATT),
    "inverter_tracker_3_maxpower_today": RegisterInfo(3159, UINT16, UnitOfPower.WATT),
    "inverter_tracker_0_maxpower_yesterday": RegisterInfo(
        3160, UINT16, UnitOfPower.WATT
    ),
    "inverter_tracker_1_maxpower_yesterday": RegisterInfo(
        3161, UINT16, UnitOfPower.WATT
    ),
    "inverter_tracker_2_maxpower_yesterday": RegisterInfo(
        3162, UINT16, UnitOfPower.WATT
    ),
    "inverter_tracker_3_maxpower_yesterday": RegisterInfo(
        3163, UINT16, UnitOfPower.WATT
    ),
    "inverter_tracker_0_power": RegisterInfo(3164, UINT16, UnitOfPower.WATT),
    "inverter_tracker_1_power": RegisterInfo(3165, UINT16, UnitOfPower.WATT),
    "inverter_tracker_2_power": RegisterInfo(3166, UINT16, UnitOfPower.WATT),
    "inverter_tracker_3_power": RegisterInfo(3167, UINT16, UnitOfPower.WATT),
    "inverter_alarm_lowsoc": RegisterInfo(
        register=3168,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class genset_status(Enum):
    """Genset status."""

    standby = 0
    startup_1 = 1
    startup_2 = 2
    startup_3 = 3
    startup_4 = 4
    startup_5 = 5
    startup_6 = 6
    startup_7 = 7
    running = 8
    stopping = 9
    error = 10


class genset_errorcode(Enum):
    """Genset error code."""

    none = 0
    ac_l1_voltage_too_low = 1
    ac_l1_frequency_too_low = 2
    ac_l1_current_too_low = 3
    ac_l1_power_too_low = 4
    emergency_stop = 5
    servo_current_too_low = 6
    oil_pressure_too_low = 7
    engine_temperature_too_low = 8
    winding_temperature_too_low = 9
    exhaust_temperature_too_low = 10
    starter_current_too_low = 13
    glow_current_too_low = 14
    glow_current_too_low_duplicate_1 = 15
    fuel_holding_magnet_current_too_low = 16
    stop_solenoid_hold_coil_current_too_low = 17
    stop_solenoid_pull_coil_current_too_low = 18
    optional_dc_out_current_too_low = 19
    output_5v_voltage_too_low = 20
    boost_output_current_too_low = 21
    panel_supply_current_too_high = 22
    starter_battery_voltage_too_low = 25
    rotation_too_low_startup_aborted = 26
    rotation_too_low = 28
    power_contacter_current_too_low = 29
    ac_l2_voltage_too_low = 30
    ac_l2_frequency_too_low = 31
    ac_l2_current_too_low = 32
    ac_l2_power_too_low = 33
    ac_l3_voltage_too_low = 34
    ac_l3_frequency_too_low = 35
    ac_l3_current_too_low = 36
    ac_l3_power_too_low = 37
    fuel_temperature_too_low = 62
    fuel_level_too_low = 63
    ac_l1_voltage_too_high = 65
    ac_l1_frequency_too_high = 66
    ac_l1_current_too_high = 67
    ac_l1_power_too_high = 68
    servo_current_too_high = 70
    oil_pressure_too_high = 71
    engine_temperature_too_high = 72
    winding_temperature_too_high = 73
    exhaust_temperature_too_high = 74  # NOTE modbustcp spec says it should be too low but that is already specified in the low grouping therefore assuming this state is used for HIGH temp
    starter_current_too_high = 77  # NOTE same as 74 applies here
    glow_current_too_high = 78
    glow_current_too_high_duplicate_1 = 79
    fuel_holding_magnet_current_too_high = 80
    stop_solenoid_hold_coil_current_too_high = 81
    stop_solenoid_pull_coil_current_too_high = 82
    optional_dc_out_current_too_high = 83
    output_5v_too_high = 84
    boost_output_current_too_high = 85
    starter_battery_voltage_too_high = 89
    rotation_too_high_startup_aborted = 90
    rotation_too_high = 92
    power_contacter_current_too_high = 93
    ac_l2_voltage_too_high = 94
    ac_l2_frequency_too_high = 95
    ac_l2_current_too_high = 96
    ac_l2_power_too_high = 97
    ac_l3_voltage_too_high = 98
    ac_l3_frequency_too_high = 99
    ac_l3_current_too_high = 100
    ac_l3_power_too_high = 101
    fuel_temperature_too_high = 126
    fuel_level_too_high = 127
    lost_control_unit = 130
    lost_panel = 131
    service_needed = 132
    lost_three_phase_module = 133
    lost_agt_module = 134
    synchronization_failure = 135
    intake_airfilter = 137
    lost_sync_module = 139
    load_balance_failed = 140
    sync_mode_deactivated = 141
    engine_controller = 142
    rotating_field_wrong = 148
    fuel_level_sensor_lost = 149
    init_failed = 150
    watchdog = 151
    outage_winding = 152
    outage_exhaust = 153
    outage_cycle_head = 154
    inverter_over_temperature = 155
    inverter_overload = 156
    inverter_commmunication_lost = 157
    inverter_sync_failed = 158
    can_communication_lost = 159
    l1_overload = 160
    l2_overload = 161
    l3_overload = 162
    dc_overload = 163
    dc_overvoltage = 164
    emergency_stop_duplicate_1 = 165
    no_connection = 166


genset_registers = {
    "genset_L1_voltage": RegisterInfo(3200, UINT16, UnitOfElectricPotential.VOLT, 10),
    "genset_L2_voltage": RegisterInfo(3201, UINT16, UnitOfElectricPotential.VOLT, 10),
    "genset_L3_voltage": RegisterInfo(3202, UINT16, UnitOfElectricPotential.VOLT, 10),
    "genset_L1_current": RegisterInfo(3203, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "genset_L2_current": RegisterInfo(3204, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "genset_L3_current": RegisterInfo(3205, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "genset_L1_power": RegisterInfo(3206, INT16, UnitOfPower.WATT),
    "genset_L2_power": RegisterInfo(3207, INT16, UnitOfPower.WATT),
    "genset_L3_power": RegisterInfo(3208, INT16, UnitOfPower.WATT),
    "genset_L1_frequency": RegisterInfo(3209, UINT16, UnitOfFrequency.HERTZ, 100),
    "genset_L2_frequency": RegisterInfo(3210, UINT16, UnitOfFrequency.HERTZ, 100),
    "genset_L3_frequency": RegisterInfo(3211, UINT16, UnitOfFrequency.HERTZ, 100),
    "genset_productid": RegisterInfo(3212, UINT16),
    "genset_statuscode": RegisterInfo(
        register=3213, dataType=UINT16, entityType=TextReadEntityType(genset_status)
    ),
    "genset_errorcode": RegisterInfo(
        register=3214, dataType=UINT16, entityType=TextReadEntityType(genset_errorcode)
    ),
    "genset_autostart": RegisterInfo(
        register=3215, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "genset_engine_load": RegisterInfo(3216, UINT16, PERCENTAGE),
    "genset_engine_speed": RegisterInfo(3217, UINT16, REVOLUTIONS_PER_MINUTE),
    "genset_engine_operatinghours": RegisterInfo(
        3218, UINT16, UnitOfTime.SECONDS, 0.01
    ),
    "genset_engine_coolanttemperature": RegisterInfo(
        3219, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "genset_engine_windingtemperature": RegisterInfo(
        3220, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "genset_engine_exhausttemperature": RegisterInfo(
        3221, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "genset_startervoltage": RegisterInfo(
        3222, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "genset_start": RegisterInfo(
        register=3223, dataType=UINT16, entityType=SwitchWriteType()
    ),
}


class temperature_type(Enum):
    """Temperature type."""

    battery = 0
    fridge = 1
    generic = 2


class temperature_status(Enum):
    """Temperature status."""

    ok = 0
    disconnected = 1
    short_circuited = 2
    reverse_polarity = 3
    unknown = 4
    low_battery = 5


temperature_registers = {
    "temperature_productid": RegisterInfo(3300, UINT16),
    "temperature_scale": RegisterInfo(3301, UINT16, "", 100),
    "temperature_offset": RegisterInfo(3302, INT16, "", 100),
    "temperature_type": RegisterInfo(
        register=3303, dataType=UINT16, entityType=TextReadEntityType(temperature_type)
    ),
    "temperature_temperature": RegisterInfo(
        3304, INT16, UnitOfTemperature.CELSIUS, 100
    ),
    "temperature_status": RegisterInfo(
        register=3305,
        dataType=UINT16,
        entityType=TextReadEntityType(temperature_status),
    ),
    "temperature_humidity": RegisterInfo(3306, UINT16, PERCENTAGE, 10),
    "temperature_batteryvoltage": RegisterInfo(
        3307, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "temperature_pressure": RegisterInfo(3308, UINT16, UnitOfPressure.HPA),
}

pulsemeter_registers = {
    "pulsemeter_aggregate": RegisterInfo(3400, UINT32, UnitOfVolume.CUBIC_METERS),
    "pulsemeter_count": RegisterInfo(3402, UINT32),
}


class digitalinput_state(Enum):
    """Digital input state."""

    low = 0
    high = 1
    off = 2
    on = 3
    no = 4
    yes = 5
    open = 6
    closed = 7
    alarm = 8
    ok = 9
    running = 10
    stopped = 11


class digitalinput_type(Enum):
    """Digital input type."""

    door = 2
    bilge_pump = 3
    bilge_alarm = 4
    burglar_alarm = 5
    smoke_alarm = 6
    fire_alarm = 7
    co2_alarm = 8


digitalinput_registers = {
    "digitalinput_count": RegisterInfo(3420, UINT32),
    "digitalinput_state": RegisterInfo(
        register=3422,
        dataType=UINT16,
        entityType=TextReadEntityType(digitalinput_state),
    ),
    "digitalinput_alarm": RegisterInfo(
        register=3423,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "digitalinput_type": RegisterInfo(
        register=3424, dataType=UINT16, entityType=TextReadEntityType(digitalinput_type)
    ),
}


class generator_runningbyconditioncode(Enum):
    """Generator running by condition code."""

    stopped = 0
    manual = 1
    test_run = 2
    loss_of_comms = 3
    soc = 4
    ac_load = 5
    battery_current = 6
    battery_voltage = 7
    inverter_temperature = 8
    inverter_overload = 9
    stop_on_ac1 = 10


class generator_state(Enum):
    """Generator state."""

    stopped = 0
    running = 1
    error = 10


class generator_error(Enum):
    """Generator error."""

    none = 0
    remote_disabled = 1
    remote_fault = 2


generator_registers = {
    "generator_manualstart": RegisterInfo(
        register=3500, dataType=UINT16, entityType=SwitchWriteType()
    ),
    "generator_runningbyconditioncode": RegisterInfo(
        register=3501,
        dataType=UINT16,
        entityType=TextReadEntityType(generator_runningbyconditioncode),
    ),
    "generator_runtime": RegisterInfo(3502, UINT16, UnitOfTime.SECONDS),
    "generator_quiethours": RegisterInfo(
        register=3503, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "generator_runtime_2": RegisterInfo(3504, UINT32, UnitOfTime.SECONDS),
    "generator_state": RegisterInfo(
        register=3506, dataType=UINT16, entityType=TextReadEntityType(generator_state)
    ),
    "generator_error": RegisterInfo(
        register=3507, dataType=UINT16, entityType=TextReadEntityType(generator_error)
    ),
    "generator_alarm_nogeneratoratacin": RegisterInfo(
        register=3508,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "generator_autostartenabled": RegisterInfo(
        register=3509, dataType=UINT16, entityType=SwitchWriteType()
    ),
}

# not processed yet
meteo_registers = {
    "meteo_irradiance": RegisterInfo(
        3600, UINT16, UnitOfIrradiance.WATTS_PER_SQUARE_METER, 10
    ),
    "meteo_windspeed": RegisterInfo(3601, UINT16, UnitOfSpeed.METERS_PER_SECOND, 10),
    "meteo_celltemperature": RegisterInfo(3602, INT16, UnitOfTemperature.CELSIUS, 10),
    "meteo_externaltemperature": RegisterInfo(
        3603, INT16, UnitOfTemperature.CELSIUS, 10
    ),
}

evcharger_productid_registers = {"evcharger_productid": RegisterInfo(3800, UINT16)}


class evcharger_mode(Enum):
    """EV charger mode."""

    manual = 0
    auto = 1
    scheduled = 2


class evcharger_status(Enum):
    """EV charger status."""

    disconnected = 0
    connected = 1
    charging = 2
    charged = 3
    waiting_for_sun = 4
    waiting_for_rfid = 5
    waiting_for_start = 6
    low_soc = 7
    ground_fault = 8
    welded_contacts = 9
    cp_input_shorted = 10
    residual_current_detected = 11
    under_voltage_detected = 12
    overvoltage_detected = 13
    overheating_detected = 14


evcharger_registers = {
    "evcharger_firmwareversion": RegisterInfo(3802, UINT32),
    "evcharger_serial": RegisterInfo(3804, STRING(6)),
    "evcharger_model": RegisterInfo(3810, STRING(4)),
    "evcharger_maxcurrent": RegisterInfo(
        register=3814,
        dataType=UINT16,
        unit=UnitOfElectricCurrent.AMPERE,
        entityType=SliderWriteType("AC", False),
    ),
    "evcharger_mode": RegisterInfo(
        register=3815, dataType=UINT16, entityType=SelectWriteType(evcharger_mode)
    ),
    "evcharger_energy_forward": RegisterInfo(
        3816, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "evcharger_L1_power": RegisterInfo(3818, UINT16, UnitOfPower.WATT),
    "evcharger_L2_power": RegisterInfo(3819, UINT16, UnitOfPower.WATT),
    "evcharger_L3_power": RegisterInfo(3820, UINT16, UnitOfPower.WATT),
    "evcharger_total_power": RegisterInfo(3821, UINT16, UnitOfPower.WATT),
    "evcharger_chargingtime": RegisterInfo(3822, UINT16, UnitOfTime.SECONDS, 0.01),
    "evcharger_current": RegisterInfo(3823, UINT16, UnitOfElectricCurrent.AMPERE),
    "evcharger_status": RegisterInfo(
        register=3824, dataType=UINT16, entityType=TextReadEntityType(evcharger_status)
    ),
    "evcharger_setcurrent": RegisterInfo(
        register=3825,
        dataType=UINT16,
        unit=UnitOfElectricCurrent.AMPERE,
        entityType=SliderWriteType("AC", False),
    ),
    "evcharger_startstop": RegisterInfo(
        register=3826, dataType=UINT16, entityType=SwitchWriteType()
    ),
    "evcharger_position": RegisterInfo(
        register=3827, dataType=UINT16, entityType=TextReadEntityType(generic_position)
    ),
}

acload_registers = {
    "acload_L1_power": RegisterInfo(3900, UINT16, UnitOfPower.WATT),
    "acload_L2_power": RegisterInfo(3901, UINT16, UnitOfPower.WATT),
    "acload_L3_power": RegisterInfo(3902, UINT16, UnitOfPower.WATT),
    "acload_serial": RegisterInfo(3903, STRING(7)),
    "acload_L1_voltage": RegisterInfo(3910, UINT16, UnitOfElectricPotential.VOLT, 10),
    "acload_L1_current": RegisterInfo(3911, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "acload_L2_voltage": RegisterInfo(3912, UINT16, UnitOfElectricPotential.VOLT, 10),
    "acload_L2_current": RegisterInfo(3913, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "acload_L3_voltage": RegisterInfo(3914, UINT16, UnitOfElectricPotential.VOLT, 10),
    "acload_L3_current": RegisterInfo(3915, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "acload_L1_energy_forward": RegisterInfo(
        3916, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "acload_L2_energy_forward": RegisterInfo(
        3918, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "acload_L3_energy_forward": RegisterInfo(
        3920, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
}

fuelcell_registers = {
    "fuelcell_battery_voltage": RegisterInfo(
        4000, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "fuelcell_battery_current": RegisterInfo(
        4001, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "fuelcell_starter_voltage": RegisterInfo(
        4002, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "fuelcell_temperature": RegisterInfo(4003, INT16, UnitOfTemperature.CELSIUS, 10),
    "fuelcell_history_energyout": RegisterInfo(
        4004, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "fuelcell_alarm_lowvoltage": RegisterInfo(
        register=4006,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "fuelcell_alarm_highvoltage": RegisterInfo(
        register=4007,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "fuelcell_alarm_lowstartervoltage": RegisterInfo(
        register=4008,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "fuelcell_alarm_highstartervoltage": RegisterInfo(
        register=4009,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "fuelcell_alarm_lowtemperature": RegisterInfo(
        register=4010,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "fuelcell_alarm_hightemperature": RegisterInfo(
        register=4011,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class alternator_state(Enum):
    """Alternator state."""

    off = 0
    fault = 2
    bulk = 3
    absorption = 4
    float = 5
    storage = 6
    equalize = 7
    external_control = 252


class alternator_errorcode(Enum):
    """Alternator error code."""

    high_battery_temperature = 12
    high_battery_voltage = 13
    low_battery_voltage = 14
    vbat_exceeds_cpb = 15
    high_alternator_temperature = 21
    alternator_overspeed = 22
    internal_error = 24
    high_field_fet_temperature = 41
    sensor_missing = 42
    low_valt = 43
    high_voltage_offset = 44
    valt_exceeds_cpb = 45
    battery_disconnect_request = 51
    battery_disconnect_request_duplicate_1 = 52
    battery_instance_out_of_range = 53
    too_many_bmses = 54
    aebus_fault = 55
    too_many_victron_devices = 56
    battery_requested_disconnection = 58
    battery_requested_disconnection_duplicate_1 = 59
    battery_requested_disconnection_duplicate_2 = 60
    battery_requested_disconnection_duplicate_3 = 61
    bms_lost = 91
    forced_idle = 92
    dcdc_converter_fail = 201
    dcdc_error = 202
    dcdc_error_duplicate_1 = 203
    dcdc_error_duplicate_2 = 204
    dcdc_error_duplicate_3 = 205
    dcdc_error_duplicate_4 = 206
    dcdc_error_duplicate_5 = 207


alternator_registers = {
    "alternator_battery_voltage": RegisterInfo(
        4100, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "alternator_battery_current": RegisterInfo(
        4101, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "alternator_startervoltage": RegisterInfo(
        4102, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "alternator_temperature": RegisterInfo(4103, INT16, UnitOfTemperature.CELSIUS, 10),
    "alternator_history_energyout": RegisterInfo(
        4104, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "alternator_alarm_lowvoltage": RegisterInfo(
        register=4106,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_alarm_highvoltage": RegisterInfo(
        register=4107,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_alarm_lowstartervoltage": RegisterInfo(
        register=4108,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_alarm_highstartervoltage": RegisterInfo(
        register=4109,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_alarm_lowtemperature": RegisterInfo(
        register=4110,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_alarm_hightemperature": RegisterInfo(
        register=4111,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "alternator_state": RegisterInfo(
        register=4112, dataType=UINT16, entityType=TextReadEntityType(alternator_state)
    ),
    "alternator_errorcode": RegisterInfo(
        register=4113,
        dataType=UINT16,
        entityType=TextReadEntityType(alternator_errorcode),
    ),
    "alternator_engine_speed": RegisterInfo(4114, UINT16, REVOLUTIONS_PER_MINUTE),
    "alternator_alternator_speed": RegisterInfo(4115, UINT16, REVOLUTIONS_PER_MINUTE),
    "alternator_fielddrive": RegisterInfo(4116, UINT16, PERCENTAGE),
}

dcsource_registers = {
    "dcsource_battery_voltage": RegisterInfo(
        4200, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcsource_battery_current": RegisterInfo(
        4201, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "dcsource_starter_voltage": RegisterInfo(
        4202, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "dcsource_temperature": RegisterInfo(4203, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcsource_history_energyout": RegisterInfo(
        4204, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "dcsource_alarm_lowvoltage": RegisterInfo(
        register=4206,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsource_alarm_highvoltage": RegisterInfo(
        register=4207,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsource_alarm_lowstartervoltage": RegisterInfo(
        register=4208,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsource_alarm_highstartervoltage": RegisterInfo(
        register=4209,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsource_alarm_lowtemperature": RegisterInfo(
        register=4210,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsource_alarm_hightemperature": RegisterInfo(
        register=4211,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}

dcload_registers = {
    "dcload_battery_voltage": RegisterInfo(
        4300, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcload_battery_current": RegisterInfo(
        4301, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "dcload_starter_voltage": RegisterInfo(
        4302, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcload_temperature": RegisterInfo(4303, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcload_history_energyin": RegisterInfo(
        4304, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "dcload_alarm_lowvoltage": RegisterInfo(
        register=4306,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcload_alarm_highvoltage": RegisterInfo(
        register=4307,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcload_alarm_lowstartervoltage": RegisterInfo(
        register=4308,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcload_alarm_highstartervoltage": RegisterInfo(
        register=4309,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcload_alarm_lowtemperature": RegisterInfo(
        register=4310,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcload_alarm_hightemperature": RegisterInfo(
        register=4311,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}

dcsystem_registers = {
    "dcsystem_battery_voltage": RegisterInfo(
        4400, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcsystem_battery_current": RegisterInfo(
        4401, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "dcsystem_starter_voltage": RegisterInfo(
        4402, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcsystem_temperature": RegisterInfo(4403, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcsystem_history_energyout": RegisterInfo(
        4404, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "dcsystem_history_energyin": RegisterInfo(
        4406, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "dcsystem_alarm_lowvoltage": RegisterInfo(
        register=4408,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsystem_alarm_highvoltage": RegisterInfo(
        register=4409,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsystem_alarm_lowstartervoltage": RegisterInfo(
        register=4410,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsystem_alarm_highstartervoltage": RegisterInfo(
        register=4411,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsystem_alarm_lowtemperature": RegisterInfo(
        register=4412,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "dcsystem_alarm_hightemperature": RegisterInfo(
        register=4413,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class multi_mode(Enum):
    """Multi mode."""

    charger = 1
    inverter = 2
    on = 3
    off = 4


class multi_input_type(Enum):
    """Multi input type."""

    unused = 0
    grid = 1
    genset = 2
    shore = 3


multi_registers = {
    "multi_input_L1_voltage": RegisterInfo(
        4500, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_input_L2_voltage": RegisterInfo(
        4501, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_input_L3_voltage": RegisterInfo(
        4502, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_input_L1_current": RegisterInfo(
        4503, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_input_L2_current": RegisterInfo(
        4504, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_input_L3_current": RegisterInfo(
        4505, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_input_L1_power": RegisterInfo(4506, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L2_power": RegisterInfo(4507, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L3_power": RegisterInfo(4508, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L1_frequency": RegisterInfo(4509, UINT16, UnitOfFrequency.HERTZ, 100),
    "multi_output_L1_voltage": RegisterInfo(
        4510, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_output_L2_voltage": RegisterInfo(
        4511, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_output_L3_voltage": RegisterInfo(
        4512, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_output_L1_current": RegisterInfo(
        4513, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_output_L2_current": RegisterInfo(
        4514, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_output_L3_current": RegisterInfo(
        4515, UINT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_output_L1_power": RegisterInfo(4516, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L2_power": RegisterInfo(4517, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L3_power": RegisterInfo(4518, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L1_frequency": RegisterInfo(4519, UINT16, UnitOfFrequency.HERTZ, 100),
    "multi_input_1_type": RegisterInfo(
        register=4520, dataType=UINT16, entityType=TextReadEntityType(multi_input_type)
    ),
    "multi_input_2_type": RegisterInfo(
        register=4521, dataType=UINT16, entityType=TextReadEntityType(multi_input_type)
    ),
    "multi_input_1_currentlimit": RegisterInfo(
        4522, UINT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", False)
    ),
    "multi_input_2_currentlimit": RegisterInfo(
        4523, UINT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", False)
    ),
    "multi_numberofphases": RegisterInfo(4524, UINT16),
    "multi_activein_activeinput": RegisterInfo(
        register=4525,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_activeinput),
    ),
    "multi_battery_voltage": RegisterInfo(
        4526, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "multi_battery_current": RegisterInfo(
        4527, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "multi_battery_temperature": RegisterInfo(
        4528, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "multi_battery_soc": RegisterInfo(4529, UINT16, PERCENTAGE, 10),
    "multi_state": RegisterInfo(
        register=4530,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_state),
    ),
    "multi_mode": RegisterInfo(
        register=4531, dataType=UINT16, entityType=SelectWriteType(multi_mode)
    ),
    "multi_alarm_hightemperature": RegisterInfo(
        register=4532,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_highvoltage": RegisterInfo(
        register=4533,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_highvoltageacout": RegisterInfo(
        register=4534,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_lowtemperature": RegisterInfo(
        register=4535,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_lowvoltage": RegisterInfo(
        register=4536,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_lowvoltageacout": RegisterInfo(
        register=4537,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_overload": RegisterInfo(
        register=4538,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_alarm_ripple": RegisterInfo(
        register=4539,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
    "multi_yield_pv_power": RegisterInfo(4540, UINT16, UnitOfPower.WATT),
    "multi_yield_user": RegisterInfo(4541, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_relay": RegisterInfo(
        register=4542, dataType=UINT16, entityType=BoolReadEntityType()
    ),
    "multi_mppoperationmode": RegisterInfo(
        register=4543,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_mppoperationmode),
    ),
    "multi_pv_voltage": RegisterInfo(4544, UINT16, UnitOfElectricPotential.VOLT, 10),
    "multi_errorcode": RegisterInfo(
        register=4545,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_charger_errorcode),
    ),
    "multi_energy_acin1toacout": RegisterInfo(
        4546, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_acin1toinverter": RegisterInfo(
        4548, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_acin2toacout": RegisterInfo(
        4550, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_acin2toinverter": RegisterInfo(
        4552, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_acouttoacin1": RegisterInfo(
        4554, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_acouttoacin2": RegisterInfo(
        4556, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_invertertoacin1": RegisterInfo(
        4558, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_invertertoacin2": RegisterInfo(
        4560, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_invertertoacout": RegisterInfo(
        4562, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_outtoinverter": RegisterInfo(
        4564, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_solartoacin1": RegisterInfo(
        4566, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_solartoacin2": RegisterInfo(
        4568, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_energy_solartoacout": RegisterInfo(
        4570, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "mutli_energy_solartobattery": RegisterInfo(
        4572, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "multi_history_yield_today": RegisterInfo(
        4574, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_maxpower_today": RegisterInfo(4575, UINT16, UnitOfPower.WATT),
    "multi_history_yield_yesterday": RegisterInfo(
        4576, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_maxpower_yesterday": RegisterInfo(4577, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_0_yield_today": RegisterInfo(
        4578, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_1_yield_today": RegisterInfo(
        4579, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_2_yield_today": RegisterInfo(
        4580, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_3_yield_today": RegisterInfo(
        4581, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_0_yield_yesterday": RegisterInfo(
        4582, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_1_yield_yesterday": RegisterInfo(
        4583, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_2_yield_yesterday": RegisterInfo(
        4584, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_3_yield_yesterday": RegisterInfo(
        4585, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "multi_history_tracker_0_maxpower_today": RegisterInfo(
        4586, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_1_maxpower_today": RegisterInfo(
        4587, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_2_maxpower_today": RegisterInfo(
        4588, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_3_maxpower_today": RegisterInfo(
        4589, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_0_maxpower_yesterday": RegisterInfo(
        4590, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_1_maxpower_yesterday": RegisterInfo(
        4591, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_2_maxpower_yesterday": RegisterInfo(
        4592, UINT16, UnitOfPower.WATT
    ),
    "multi_history_tracker_3_maxpower_yesterday": RegisterInfo(
        4593, UINT16, UnitOfPower.WATT
    ),
    "multi_tracker_0_voltage": RegisterInfo(
        4594, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_tracker_1_voltage": RegisterInfo(
        4595, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_tracker_2_voltage": RegisterInfo(
        4596, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_tracker_3_voltage": RegisterInfo(
        4597, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "multi_tracker_0_power": RegisterInfo(4598, UINT16, UnitOfPower.WATT),
    "multi_tracker_1_power": RegisterInfo(4599, UINT16, UnitOfPower.WATT),
    "multi_tracker_2_power": RegisterInfo(4600, UINT16, UnitOfPower.WATT),
    "multi_tracker_3_power": RegisterInfo(4601, UINT16, UnitOfPower.WATT),
    "multi_alarm_lowsoc": RegisterInfo(
        register=4602,
        dataType=UINT16,
        entityType=TextReadEntityType(generic_alarm_ledger),
    ),
}


class register_input_source(Enum):
    """Input source."""

    unknown = 0
    grid = 1
    generator = 2
    shore = 3
    not_connected = 240


system_registers = {
    "system_serial": RegisterInfo(800, STRING(6)),
    "system_relay_0": RegisterInfo(
        register=806, dataType=UINT16, entityType=SwitchWriteType()
    ),
    "system_relay_1": RegisterInfo(
        register=807, dataType=UINT16, entityType=SwitchWriteType()
    ),
    "system_pvonoutput_L1": RegisterInfo(808, UINT16, UnitOfPower.WATT),
    "system_pvonoutput_L2": RegisterInfo(809, UINT16, UnitOfPower.WATT),
    "system_pvonoutput_L3": RegisterInfo(810, UINT16, UnitOfPower.WATT),
    "system_pvongrid_L1": RegisterInfo(811, UINT16, UnitOfPower.WATT),
    "system_pvongrid_L2": RegisterInfo(812, UINT16, UnitOfPower.WATT),
    "system_pvongrid_L3": RegisterInfo(813, UINT16, UnitOfPower.WATT),
    "system_pvongenset_L1": RegisterInfo(814, UINT16, UnitOfPower.WATT),
    "system_pvongenset_L2": RegisterInfo(815, UINT16, UnitOfPower.WATT),
    "system_pvongenset_L3": RegisterInfo(816, UINT16, UnitOfPower.WATT),
    "system_consumption_L1": RegisterInfo(817, UINT16, UnitOfPower.WATT),
    "system_consumption_L2": RegisterInfo(818, UINT16, UnitOfPower.WATT),
    "system_consumption_L3": RegisterInfo(819, UINT16, UnitOfPower.WATT),
    "system_grid_L1": RegisterInfo(820, INT16, UnitOfPower.WATT),
    "system_grid_L2": RegisterInfo(821, INT16, UnitOfPower.WATT),
    "system_grid_L3": RegisterInfo(822, INT16, UnitOfPower.WATT),
    "system_genset_L1": RegisterInfo(823, INT16, UnitOfPower.WATT),
    "system_genset_L2": RegisterInfo(824, INT16, UnitOfPower.WATT),
    "system_genset_L3": RegisterInfo(825, INT16, UnitOfPower.WATT),
    "system_input_source": RegisterInfo(
        register=826,
        dataType=INT16,
        entityType=TextReadEntityType(register_input_source),
    ),
}


class system_battery_state(Enum):
    """Battery state."""

    idle = 0
    charging = 1
    discharging = 2


system_battery_registers = {
    "system_battery_voltage": RegisterInfo(
        840, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "system_battery_current": RegisterInfo(
        841, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "system_battery_power": RegisterInfo(842, INT16, UnitOfPower.WATT),
    "system_battery_soc": RegisterInfo(843, UINT16, PERCENTAGE),
    "system_battery_state": RegisterInfo(
        register=844,
        dataType=UINT16,
        entityType=TextReadEntityType(system_battery_state),
    ),
    "system_battery_amphours": RegisterInfo(
        845, UINT16, UnitOfElectricCurrent.AMPERE, -10
    ),  #  NOTE should be amp hours
    "system_battery_time_to_go": RegisterInfo(846, UINT16, UnitOfTime.SECONDS, 0.01),
}

system_dc_registers = {
    "system_dc_pv_power": RegisterInfo(850, UINT16, UnitOfPower.WATT),
    "system_dc_pv_current": RegisterInfo(851, INT16, UnitOfElectricCurrent.AMPERE, 10),
}

system_charger_registers = {
    "system_charger_power": RegisterInfo(855, UINT16, UnitOfPower.WATT)
}

system_power_registers = {
    "system_system_power": RegisterInfo(860, INT16, UnitOfPower.WATT)
}

system_bus_registers = {
    "system_bus_charge_current": RegisterInfo(
        865, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "system_bus_charge_power": RegisterInfo(866, INT16, UnitOfPower.WATT),
}

valid_unit_ids = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    100,
    101,
    204,
    205,
    206,
    207,
    208,
    209,
    210,
    211,
    212,
    213,
    214,
    215,
    216,
    217,
    218,
    219,
    220,
    221,
    222,
    223,
    224,
    225,
    226,
    227,
    228,
    229,
    230,
    231,
    232,
    233,
    234,
    235,
    236,
    237,
    238,
    239,
    242,
    243,
    245,
    246,
    247,
]

register_info_dict = {
    "gavazi_grid_registers": gavazi_grid_registers,
    "vebus_registers": vebus_registers,
    "battery_registers": battery_registers,
    "battery_detail_registers": battery_detail_registers,
    "solarcharger_registers": solarcharger_registers,
    "solarcharger_tracker_voltage_registers": solarcharger_tracker_voltage_registers,
    "solarcharger_tracker_registers": solarcharger_tracker_registers,
    "pvinverter_registers": pvinverter_registers,
    "motordrive_registers": motordrive_registers,
    "charger_registers": charger_registers,
    "settings_registers": settings_registers,
    "gps_registers": gps_registers,
    "settings_ess_registers": settings_ess_registers,
    "tank_registers": tank_registers,
    "inverter_output_registers": inverter_output_registers,
    "inverter_battery_registers": inverter_battery_registers,
    "inverter_alarm_registers": inverter_alarm_registers,
    "inverter_info_registers": inverter_info_registers,
    "inverter_energy_registers": inverter_energy_registers,
    "inverter_tracker_registers": inverter_tracker_registers,
    "inverter_tracker_statistics_registers": inverter_tracker_statistics_registers,
    "genset_registers": genset_registers,
    "temperature_registers": temperature_registers,
    "pulsemeter_registers": pulsemeter_registers,
    "digitalinput_registers": digitalinput_registers,
    "generator_registers": generator_registers,
    "meteo_registers": meteo_registers,
    "evcharger_productid_registers": evcharger_productid_registers,
    "evcharger_registers": evcharger_registers,
    "acload_registers": acload_registers,
    "fuelcell_registers": fuelcell_registers,
    "alternator_registers": alternator_registers,
    "dcsource_registers": dcsource_registers,
    "dcload_registers": dcload_registers,
    "dcsystem_registers": dcsystem_registers,
    "multi_registers": multi_registers,
    "system_registers": system_registers,
    "system_battery_registers": system_battery_registers,
    "system_dc_registers": system_dc_registers,
    "system_charger_registers": system_charger_registers,
    "system_power_registers": system_power_registers,
    "system_bus_registers": system_bus_registers,
}
