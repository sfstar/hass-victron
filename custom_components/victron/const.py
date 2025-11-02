"""Constants for the victron integration."""

from enum import Enum

from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
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

    GRID = 1
    TANK = 2
    MULTI = 3
    VEBUS = 4


AMPHOURS = "Ah"
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
INT64 = "int64"
UINT64 = "uint64"

UINT16_MAX = 65535


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

    OK = 0
    WARNING = 1
    ALARM = 2


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
    "grid_ac_L1_power": RegisterInfo(2638, INT32, UnitOfPower.WATT),
    "grid_ac_L2_power": RegisterInfo(2640, INT32, UnitOfPower.WATT),
    "grid_ac_L3_power": RegisterInfo(2642, INT32, UnitOfPower.WATT),
    "grid_ac_frequency": RegisterInfo(2644, UINT16, UnitOfFrequency.HERTZ, 100),
}

gavazi_grid_registers_2 = {
    "grid_L1_powerfactor": RegisterInfo(2645, INT16, "", 1000),
    "grid_L2_powerfactor": RegisterInfo(2646, INT16, "", 1000),
    "grid_L3_powerfactor": RegisterInfo(2647, INT16, "", 1000),
    "grid_total_powerfactor": RegisterInfo(2648, INT16, "", 1000),
}


class vebus_mode(Enum):
    """Vebus mode."""

    CHARGER = 1
    INVERTER = 2
    ON = 3
    OFF = 4


class generic_activeinput(Enum):
    """Generic active input."""

    AC_INPUT_1 = 0
    AC_INPUT_2 = 1
    DISCONNECTED = 240


class generic_charger_state(Enum):
    """Generic charger state."""

    OFF = 0
    LOW_POWER = 1
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE = 7
    PASSTHRU = 8
    INVERTING = 9
    POWER_ASSIST = 10
    POWER_SUPPLY = 11
    SUSTAIN = 244
    EXTERNAL_CONTROL = 252


class vebus_error(Enum):
    """Vebus error."""

    OK = 0
    EXTERNAL_PHASE_TRIGGERED_SWITCHOFF = 1
    MK2_TYPE_MISMATCH = 2
    DEVICE_COUNT_MISMATCH = 3
    NO_OTHER_DEVICES = 4
    AC_OVERVOLTAGE_OUT = 5
    DDC_PROGRAM = 6
    BMS_WITHOUT_ASSISTANT_CONNECTED = 7
    TIME_SYNC_MISMATCH = 10
    CANNOT_TRANSMIT = 14
    DONGLE_ABSENT = 16
    MASTER_FAILOVER = 17
    AC_OVERVOLTAGE_SLAVE_OFF = 18
    CANNOT_BE_SLAVE = 22
    SWITCH_OVER_PROTECTION = 24
    FIRMWARE_INCOMPATIBILTIY = 25
    INTERNAL_ERROR = 26


class vebus_charger_state(Enum):
    """Vebus charger state."""

    INITIALIZING = 0
    BULK = 1
    ABSORPTION = 2
    FLOAT = 3
    STORAGE = 4
    ABSORBTION_REPEAT = 5
    FORCED_ABSORBTION = 6
    EQUALIZE = 7
    BULK_STOPPED = 8
    UNKNOWN = 9


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
    "vebus_alarm_BmsPreAlarm": RegisterInfo(
        94, UINT16, entityType=TextReadEntityType(generic_alarm_ledger)
    ),
    "vebus_charge_state": RegisterInfo(
        95, UINT16, entityType=TextReadEntityType(vebus_charger_state)
    ),
    "vebus_ess_L1_acpowersetpoint": RegisterInfo(
        96,
        INT32,
        UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),  # 32 bit compliment to 37, 40 and 41
    "vebus_ess_L2_acpowersetpoint": RegisterInfo(
        98,
        INT32,
        UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "vebus_ess_L3_acpowersetpoint": RegisterInfo(
        100,
        INT32,
        UnitOfPower.WATT,
        entityType=SliderWriteType("AC", True),
    ),
    "vebus_dc_preferrenewableenergy": RegisterInfo(
        102, UINT16, entityType=SwitchWriteType()
    ),
    "vebus_ac_control_remotegeneratorselected": RegisterInfo(
        103, UINT16, entityType=SwitchWriteType()
    ),
    "vebus_ac_state_remotegeneratorselected": RegisterInfo(
        104, UINT16, entityType=BoolReadEntityType()
    ),
    "vebus_redetectsystem": RegisterInfo(105, UINT16, entityType=ButtonWriteType()),
    "vebus_settings_assistcurrentboostfactor": RegisterInfo(
        106, UINT16, scale=100, entityType=SliderWriteType(UINT16)
    ),
    "vebus_settings_inverteroutputvoltage": RegisterInfo(
        107, UINT16, UnitOfElectricPotential.VOLT, 100, entityType=SliderWriteType("AC")
    ),
    "vebus_settings_powerassistenabled": RegisterInfo(
        108, UINT16, entityType=SwitchWriteType()
    ),
    "vebus_settings_upsfunction": RegisterInfo(
        109, UINT16, entityType=SwitchWriteType()
    ),
}


class vebus_microgrid_mode(Enum):
    """Vebus microgrid mode."""

    GRID_FORMING = 0
    GRID_FOLLOWING = 1
    RESERVED = 2
    HYBRID_DROOP_MODE = 3


vebus_registers_2 = {
    "vebus_microgrid_mode": RegisterInfo(
        200, UINT16, entityType=TextReadEntityType(vebus_microgrid_mode)
    ),
    "vebus_microgrid_reference_frequency": RegisterInfo(
        201,
        INT16,
        UnitOfFrequency.HERTZ,
        100,
        entityType=SliderWriteType(UnitOfFrequency.HERTZ),
    ),
    "vebus_microgrid_reference_power": RegisterInfo(
        202, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_minimum_active_power": RegisterInfo(
        203, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_maximum_active_power": RegisterInfo(
        204, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_frequency_droop": RegisterInfo(
        205, UINT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=False)
    ),
    "vebus_microgrid_reference_reactive_power": RegisterInfo(
        206, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_minimum_reactive_power": RegisterInfo(
        207, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_maximum_reactive_power": RegisterInfo(
        208, INT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=True)
    ),
    "vebus_microgrid_voltage_droop_slope": RegisterInfo(
        209, UINT16, PERCENTAGE, 100, entityType=SliderWriteType(negative=False)
    ),
    "vebus_microgrid_reference_voltage": RegisterInfo(
        210,
        UINT16,
        UnitOfElectricPotential.VOLT,
        100,
        entityType=SliderWriteType(negative=False),
    ),
    "vebus_microgrid_activate_droop_mode_parameters": RegisterInfo(
        211, UINT16, "", 1, entityType=ButtonWriteType()
    ),
    # RESERVED 212
    "vebus_microgrid_directdrive_minimum_frequency": RegisterInfo(
        213, UINT16, UnitOfFrequency.HERTZ, 100
    ),
    "vebus_microgrid_directdrive_maximum_frequency": RegisterInfo(
        214, UINT16, UnitOfFrequency.HERTZ, 100
    ),
    "vebus_microgrid_directdrive_power_setpoint": RegisterInfo(
        215, INT16, PERCENTAGE, 100
    ),
    "vebus_microgrid_directdrive_reactive_power_setpoint": RegisterInfo(
        216, INT16, PERCENTAGE, 100
    ),
    "vebus_microgrid_directdrive_range_minimum_voltage": RegisterInfo(
        217, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "vebus_microgrid_directdrive_range_maximum_voltage": RegisterInfo(
        218, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "vebus_microgrid_directdrive_activate_grid_following_parameters": RegisterInfo(
        219, UINT16, "", 1, entityType=ButtonWriteType()
    ),
    "vebus_microgrid_directdrive_grid_forming_frequency_setpoint": RegisterInfo(
        220, UINT16, UnitOfFrequency.HERTZ, 100
    ),
    "vebus_microgrid_directdrive_grid_forming_voltage_setpoint": RegisterInfo(
        221, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "vebus_microgrid_directdrive_activate_grid_forming_parameters": RegisterInfo(
        222, UINT16, "", 1, entityType=ButtonWriteType()
    ),
    # RESERVED 223 - 229
}


class microgrid_error(Enum):
    """Microgrid error."""

    NO_ERROR = 0
    DIFFERENT_FALLBAC_PARAMETER_VALUES_BETWEEN_PHASE_MASTERS = 1
    HYBRID_DROOP_PARAMETER_WRITE_FAILED = 2


vebus_registers_4 = {
    "vebus_microgrid_heartbeat": RegisterInfo(
        230, UINT16, 1, entityType=ButtonWriteType()
    ),
    "vebus_microgrid_error": RegisterInfo(
        231, UINT16, TextReadEntityType(microgrid_error)
    ),
}


class battery_mode(Enum):
    """Battery mode."""

    OPEN = 0
    STANDBY = 14


battery_registers_0 = {
    "battery_power_int32": RegisterInfo(256, INT32, UnitOfPower.WATT)
}

battery_registers = {
    "battery_power": RegisterInfo(
        258, INT16, UnitOfPower.WATT, entityType=SliderWriteType("DC", True)
    ),
    "battery_voltage": RegisterInfo(259, UINT16, UnitOfElectricPotential.VOLT, 100),
    "battery_starter_voltage": RegisterInfo(
        260, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "battery_current": RegisterInfo(261, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "battery_temperature": RegisterInfo(262, INT16, UnitOfTemperature.CELSIUS, 10),
    "battery_midvoltage": RegisterInfo(263, UINT16, UnitOfElectricPotential.VOLT, 100),
    "battery_midvoltagedeviation": RegisterInfo(264, UINT16, PERCENTAGE, 100),
    "battery_consumedamphours": RegisterInfo(265, UINT16, AMPHOURS, -10),
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
    "battery_history_deepestdischarge": RegisterInfo(281, UINT16, AMPHOURS, -10),
    "battery_history_lastdischarge": RegisterInfo(282, UINT16, AMPHOURS, -10),
    "battery_history_averagedischarge": RegisterInfo(283, UINT16, AMPHOURS, -10),
    "battery_history_chargecycles": RegisterInfo(284, UINT16),
    "battery_history_fulldischarges": RegisterInfo(285, UINT16),
    "battery_history_totalahdrawn": RegisterInfo(286, UINT16, AMPHOURS, -10),
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
    "battery_mode": RegisterInfo(327, UINT16, entityType=SelectWriteType(battery_mode)),
}

battery_registers_2 = {
    "battery_consumedamphours_uint32": RegisterInfo(330, UINT32, AMPHOURS, -1),
}


class battery_state(Enum):
    """Battery state."""

    WAIT_START_INIT = 0
    BEFORE_BOOT_INIT = 1
    BEFORE_BOOT_DELAY_INIT = 2
    WAIT_BOOT_INIT = 3
    INITIALIZING = 4
    BATTERY_VOLTAGE_MEASURE_INIT = 5
    BATTERY_CALCULATE_VOLTAGE_INIT = 6
    WAIT_BUS_VOLTAGE_INIT = 7
    WAIT_LYNX_SHUNT_INIT = 8
    RUNNING = 9
    ERROR = 10
    UNUSED = 11
    SHUTDOWN = 12
    SLAVE_UPDATING = 13
    STANDBY = 14
    GOING_TO_RUN = 15
    PRE_CHARGING = 16
    CONTACTOR_CHECK = 17


class battery_error(Enum):
    """Battery error."""

    NONE = 0
    BATTERY_INIT_ERROR = 1
    NO_BATTERIES_CONNECTED = 2
    UNKNOWN_BATTERY_CONNECTED = 3
    DIFFERENT_BATTERY_TYPE = 4
    NUMBER_OF_BATTERIES_INCORRECT = 5
    LYNX_SHUNT_NOT_FOUND = 6
    BATTERY_MEASURE_ERROR = 7
    INTERNAL_CALCULATION_ERROR = 8
    BATTERIES_IN_SERIES_NOT_OK = 9
    NUMBER_OF_BATTERIES_INCORRECT_DUPLICATE_1 = 10
    HARDWARE_ERROR = 11
    WATCHDOG_ERROR = 12
    OVER_VOLTAGE = 13
    UNDER_VOLTAGE = 14
    OVER_TEMPERATURE = 15
    UNDER_TEMPERATURE = 16
    HARDWARE_FAULT = 17
    STANDBY_SHUTDOWN = 18
    PRE_CHARGE_CHARGE_ERROR = 19
    SAFETY_CONTACTOR_CHECK_ERROR = 20
    PRE_CHARGE_DISCHARGE_ERROR = 21
    ADC_ERROR = 22
    SLAVE_ERROR = 23
    SLAVE_WARNING = 24
    PRE_CHARGE_ERROR = 25
    SAFETY_CONTACTOR_ERROR = 26
    OVER_CURRENT = 27
    SLAVE_UPDATE_FAILED = 28
    SLAVE_UPDATE_UNAVAILABLE = 29
    CALIBRATION_DATA_LOST = 30
    SETTINGS_INVALID = 31
    BMS_CABLE = 32
    REFERENCE_FAILURE = 33
    WRONG_SYSTEM_VOLTAGE = 34
    PRE_CHARGE_TIMEOUT = 35


class battery_mode_alternative(Enum):
    """Battery mode alternative."""

    ON = 3
    STANDBY = 252


class battery_balancer_status(Enum):
    """Battery balancer status."""

    UNKNOWN = 0
    BALANCED = 1
    BALANCING = 2
    CELL_IMBALANCE = 3


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
    "battery_mode_2": RegisterInfo(
        1319, UINT16, entityType=SelectWriteType(battery_mode_alternative)
    ),
    "battery_balancer_status": RegisterInfo(
        1320, UINT16, entityType=TextReadEntityType(battery_balancer_status)
    ),
    "battery_errors_smartlithium_communication": RegisterInfo(
        1321, UINT16
    ),  # This has no decode values for returned numbers
    "battery_errors_smartlithium_voltage": RegisterInfo(
        1322, UINT16
    ),  # This has no decode values for returned numbers
    "battery_errors_smartlithium_numberofbatteries": RegisterInfo(
        1323, UINT16
    ),  # This has no decode values for returned numbers
    "battery_errors_smartlithium_invalidconfiguration": RegisterInfo(
        1324, UINT16
    ),  # This has no decode values for returned numbers
    "battery_connection_information": RegisterInfo(1328, STRING(8)),
}


class solarcharger_mode(Enum):
    """Solar charger mode."""

    ON = 1
    OFF = 4


class solarcharger_state(Enum):
    """Solar charger state."""

    OFF = 0
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE = 7
    OTHER_HUB_1 = 11
    WAKE_UP = 245
    EXTERNAL_CONTROL = 252


class solarcharger_equalization_pending(Enum):
    """Solar charger equalization pending."""

    NO = 0
    YES = 1
    ERROR = 2
    UNAVAILABLE = 3


class generic_charger_errorcode(Enum):
    """Generic charger error code."""

    NONE = 0
    TEMPERATURE_HIGH = 1
    VOLTAGE_HIGH = 2
    TEMPERATURE_SENSOR_PLUS_MISWIRED = 3
    TEMPERATURE_SENSOR_MIN_MISWIRED = 4
    TEMPERATURE_SENSOR_DISCONNECTED = 5
    VOLTAGE_SENSE_PLUS_MISWIRED = 6
    VOLTAGE_SENSE_MIN_MISWIRED = 7
    VOLTAGE_SENSE_DISCONNECTED = 8
    VOLTAGE_WIRE_LOSSES_TOO_HIGH = 9
    CHARGER_TEMPERATURE_TOO_HIGH = 17
    CHARGER_OVER_CURRENT = 18
    CHARGER_POLARITY_REVERSED = 19
    BULK_TIME_LIMIT = 20
    CHARGER_TEMPERATURE_SENSOR_MISWIRED = 22
    CHARGER_TEMPERATURE_SENSOR_DISCONNECTED = 23
    INPUT_CURRENT_TOO_HIGH = 34


class generic_mppoperationmode(Enum):
    """Generic MPP operation mode."""

    OFF = 0
    LIMITED = 1
    ACTIVE = 2
    UNAVAILABLE = 255


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

solarcharger_registers_2 = {
    "solarcharger_yield_power_uint32": RegisterInfo(792, UINT32, UnitOfPower.WATT),
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
    # RESERVED 3704
    # RESERVED 3705
    # RESERVED 3706
    # RESERVED 3707
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
    "solarcharger_yield_user": RegisterInfo(3728, UINT32, UnitOfEnergy.KILO_WATT_HOUR),
    "solarcharger_yield_pv": RegisterInfo(3730, UINT16, UnitOfPower.WATT),
    "solarcharger_pv_mppoperationmode_0": RegisterInfo(
        3731, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "solarcharger_pv_mppoperationmode_1": RegisterInfo(
        3732, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "solarcharger_pv_mppoperationmode_2": RegisterInfo(
        3733, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "solarcharger_pv_mppoperationmode_3": RegisterInfo(
        3734, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
}


class generic_position(Enum):
    """Generic position."""

    AC_INPUT_1 = 0
    AC_OUTPUT = 1
    AC_INPUT_2 = 2


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
    "pvinverter_ac_L1_power": RegisterInfo(1058, UINT32, UnitOfPower.WATT),
    "pvinverter_ac_L2_power": RegisterInfo(1060, UINT32, UnitOfPower.WATT),
    "pvinverter_ac_L3_power": RegisterInfo(1062, UINT32, UnitOfPower.WATT),
    "pvinverter_ac_frequency": RegisterInfo(1064, UINT16, UnitOfFrequency.HERTZ, 100),
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

    OFF = 0
    ON = 1
    ERROR = 2
    UNAVAILABLE = 3


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


class acinput_source(Enum):
    """AC input source."""

    UNUSED = 0
    GRID = 1
    GENSET = 2
    SHORE = 3


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
    "settings_systemssetup_acinput1": RegisterInfo(
        2711, UINT16, entityType=SelectWriteType(acinput_source)
    ),
    "settings_systemssetup_acinput2": RegisterInfo(
        2712, UINT16, entityType=SelectWriteType(acinput_source)
    ),
}

settings_cgwacs_registers = {
    # com.victronenergy.settings	AC export limit when peakshaving	2713	int16	1	-32768 to 32767	/Settings/CGwacs/AcExportLimit	yes		-1: Disabled
    # com.victronenergy.settings	AC import limit when peakshaving	2714	int16	1	-32768 to 32767	/Settings/CGwacs/AcImportLimit	yes		-1: Disabled
    "settings_cgwacs_alwayspeakshave": RegisterInfo(
        2715, UINT16, entityType=SwitchWriteType()
    ),
    "settings_overrides_setpoint_volatile": RegisterInfo(2716, INT32, UnitOfPower.WATT),
}


class without_gridmeter_options(Enum):
    """Settings CGWACS run without grid meter options."""

    EXTENRAL_METER = 0
    INVERTER_CHARGER = 1


settings_cgwacs_registers_2 = {
    "settings_cgwacs_run_without_gridmeter": RegisterInfo(
        2718, UINT16, "", 1, SelectWriteType(without_gridmeter_options)
    )
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

    BL_DISABLED_DUPLICATE_1 = 0
    RESTARTING = 1
    SELF_CONSUMPTION = 2
    SELF_CONSUMPTION_DUPLICATE_1 = 3
    SELF_CONSUMPTION_DUPLICATE_2 = 4
    DISCHARGE_DISABLED = 5
    FORCE_CHARGE = 6
    SUSTAIN = 7
    LOW_SOC_RECHARGE = 8
    KEEP_BATTERIES_CHARGED = 9
    BL_DISABLED = 10
    BL_DISABLED_LOW_SOC = 11
    BL_DISABLED_LOC_SOC_RECHARGE = 12


class ess_mode(Enum):
    """ESS mode."""

    SELF_CONSUMPTION_WITH_BATTERY_LIFE = 0
    SELF_CONSUMPTION = 1
    KEEP_CHARGED = 2
    EXTERNAL_CONTROL = 3


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

    FUEL = 0
    FRESH_WATER = 1
    WASTE_WATER = 2
    LIVE_WELL = 3
    OIL = 4
    SEWAGE_WATER = 5
    GASOLINE = 6
    DIESEL = 7
    LPG = 8
    LNG = 9
    HYDRAULIC_OIL = 10
    RAW_WATER = 11


class tank_status(Enum):
    """Tank status."""

    OK = 0
    OPEN_CIRCUIT = 1
    SHORT_CIRCUITED = 2
    REVERSE_POLARITY = 3
    UNKNOWN = 4
    ERROR = 5


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

    CHARGER_ONLY = 1
    INVERTER_ONLY = 2
    ON = 3
    OFF = 4
    LOW_POWER = 5
    PASSTHROUGH = 251
    STANDBY = 252
    HIBERNATE = 253


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
    "inverter_tracker_0_mppoperationmode": RegisterInfo(
        3169, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "inverter_tracker_1_mppoperationmode": RegisterInfo(
        3170, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "inverter_tracker_2_mppoperationmode": RegisterInfo(
        3171, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "inverter_tracker_3_mppoperationmode": RegisterInfo(
        3172, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
}


class genset_status(Enum):
    """Genset status."""

    STANDBY = 0
    STARTUP_1 = 1
    STARTUP_2 = 2
    STARTUP_3 = 3
    STARTUP_4 = 4
    STARTUP_5 = 5
    STARTUP_6 = 6
    STARTUP_7 = 7
    RUNNING = 8
    STOPPING = 9
    ERROR = 10


class genset_errorcode(Enum):
    """Genset error code."""

    NONE = 0
    AC_L1_VOLTAGE_TOO_LOW = 1
    AC_L1_FREQUENCY_TOO_LOW = 2
    AC_L1_CURRENT_TOO_LOW = 3
    AC_L1_POWER_TOO_LOW = 4
    EMERGENCY_STOP = 5
    SERVO_CURRENT_TOO_LOW = 6
    OIL_PRESSURE_TOO_LOW = 7
    ENGINE_TEMPERATURE_TOO_LOW = 8
    WINDING_TEMPERATURE_TOO_LOW = 9
    EXHAUST_TEMPERATURE_TOO_LOW = 10
    STARTER_CURRENT_TOO_LOW = 13
    GLOW_CURRENT_TOO_LOW = 14
    GLOW_CURRENT_TOO_LOW_DUPLICATE_1 = 15
    FUEL_HOLDING_MAGNET_CURRENT_TOO_LOW = 16
    STOP_SOLENOID_HOLD_COIL_CURRENT_TOO_LOW = 17
    STOP_SOLENOID_PULL_COIL_CURRENT_TOO_LOW = 18
    OPTIONAL_DC_OUT_CURRENT_TOO_LOW = 19
    OUTPUT_5V_VOLTAGE_TOO_LOW = 20
    BOOST_OUTPUT_CURRENT_TOO_LOW = 21
    PANEL_SUPPLY_CURRENT_TOO_HIGH = 22
    STARTER_BATTERY_VOLTAGE_TOO_LOW = 25
    ROTATION_TOO_LOW_STARTUP_ABORTED = 26
    ROTATION_TOO_LOW = 28
    POWER_CONTACTER_CURRENT_TOO_LOW = 29
    AC_L2_VOLTAGE_TOO_LOW = 30
    AC_L2_FREQUENCY_TOO_LOW = 31
    AC_L2_CURRENT_TOO_LOW = 32
    AC_L2_POWER_TOO_LOW = 33
    AC_L3_VOLTAGE_TOO_LOW = 34
    AC_L3_FREQUENCY_TOO_LOW = 35
    AC_L3_CURRENT_TOO_LOW = 36
    AC_L3_POWER_TOO_LOW = 37
    FUEL_TEMPERATURE_TOO_LOW = 62
    FUEL_LEVEL_TOO_LOW = 63
    AC_L1_VOLTAGE_TOO_HIGH = 65
    AC_L1_FREQUENCY_TOO_HIGH = 66
    AC_L1_CURRENT_TOO_HIGH = 67
    AC_L1_POWER_TOO_HIGH = 68
    SERVO_CURRENT_TOO_HIGH = 70
    OIL_PRESSURE_TOO_HIGH = 71
    ENGINE_TEMPERATURE_TOO_HIGH = 72
    WINDING_TEMPERATURE_TOO_HIGH = 73
    EXHAUST_TEMPERATURE_TOO_HIGH = 74  # NOTE modbustcp spec says it should be too low but that is already specified in the low grouping therefore assuming this state is used for HIGH temp
    STARTER_CURRENT_TOO_HIGH = 77  # NOTE same as 74 applies here
    GLOW_CURRENT_TOO_HIGH = 78
    GLOW_CURRENT_TOO_HIGH_DUPLICATE_1 = 79
    FUEL_HOLDING_MAGNET_CURRENT_TOO_HIGH = 80
    STOP_SOLENOID_HOLD_COIL_CURRENT_TOO_HIGH = 81
    STOP_SOLENOID_PULL_COIL_CURRENT_TOO_HIGH = 82
    OPTIONAL_DC_OUT_CURRENT_TOO_HIGH = 83
    OUTPUT_5V_TOO_HIGH = 84
    BOOST_OUTPUT_CURRENT_TOO_HIGH = 85
    STARTER_BATTERY_VOLTAGE_TOO_HIGH = 89
    ROTATION_TOO_HIGH_STARTUP_ABORTED = 90
    ROTATION_TOO_HIGH = 92
    POWER_CONTACTER_CURRENT_TOO_HIGH = 93
    AC_L2_VOLTAGE_TOO_HIGH = 94
    AC_L2_FREQUENCY_TOO_HIGH = 95
    AC_L2_CURRENT_TOO_HIGH = 96
    AC_L2_POWER_TOO_HIGH = 97
    AC_L3_VOLTAGE_TOO_HIGH = 98
    AC_L3_FREQUENCY_TOO_HIGH = 99
    AC_L3_CURRENT_TOO_HIGH = 100
    AC_L3_POWER_TOO_HIGH = 101
    FUEL_TEMPERATURE_TOO_HIGH = 126
    FUEL_LEVEL_TOO_HIGH = 127
    LOST_CONTROL_UNIT = 130
    LOST_PANEL = 131
    SERVICE_NEEDED = 132
    LOST_THREE_PHASE_MODULE = 133
    LOST_AGT_MODULE = 134
    SYNCHRONIZATION_FAILURE = 135
    INTAKE_AIRFILTER = 137
    LOST_SYNC_MODULE = 139
    LOAD_BALANCE_FAILED = 140
    SYNC_MODE_DEACTIVATED = 141
    ENGINE_CONTROLLER = 142
    ROTATING_FIELD_WRONG = 148
    FUEL_LEVEL_SENSOR_LOST = 149
    INIT_FAILED = 150
    WATCHDOG = 151
    OUTAGE_WINDING = 152
    OUTAGE_EXHAUST = 153
    OUTAGE_CYCLE_HEAD = 154
    INVERTER_OVER_TEMPERATURE = 155
    INVERTER_OVERLOAD = 156
    INVERTER_COMMMUNICATION_LOST = 157
    INVERTER_SYNC_FAILED = 158
    CAN_COMMUNICATION_LOST = 159
    L1_OVERLOAD = 160
    L2_OVERLOAD = 161
    L3_OVERLOAD = 162
    DC_OVERLOAD = 163
    DC_OVERVOLTAGE = 164
    EMERGENCY_STOP_DUPLICATE_1 = 165
    NO_CONNECTION = 166


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
    "genset_L2_frequency": RegisterInfo(
        3210, UINT16, UnitOfFrequency.HERTZ, 100
    ),  # Has later been changed to reserved from phase frequency
    "genset_L3_frequency": RegisterInfo(
        3211, UINT16, UnitOfFrequency.HERTZ, 100
    ),  # Has later been changed to reserved from phase frequency
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
        register=3223,
        dataType=UINT16,
        entityType=SwitchWriteType(),  # deprecated
    ),
    "genset_engine_oilpressure": RegisterInfo(3224, INT16, UnitOfPressure.KPA),
    # com.victronenergy.genset	RESERVED	3225	uint16	1		RESERVED	no
    # com.victronenergy.genset	RESERVED	3226	uint16	1		RESERVED	no
    # com.victronenergy.genset	RESERVED	3227	uint16	1		RESERVED	no	Degrees celsius
}


genset_registers_2 = {
    "genset_engine_oiltemperature": RegisterInfo(
        3228, INT16, UnitOfTemperature.CELSIUS, 10
    ),
}

genset_registers_4 = {
    "genset_L1_power_int32": RegisterInfo(3230, INT32, UnitOfPower.WATT),
    "genset_L2_power_int32": RegisterInfo(3232, INT32, UnitOfPower.WATT),
    "genset_L3_power_int32": RegisterInfo(3234, INT32, UnitOfPower.WATT),
    "genset_L1_powerfactor": RegisterInfo(3236, INT16, "", 1000),
    "genset_L2_powerfactor": RegisterInfo(3237, INT16, "", 1000),
    "genset_L3_powerfactor": RegisterInfo(3238, INT16, "", 1000),
    "genset_total_powerfactor": RegisterInfo(3239, INT16, "", 1000),
}

genset_thirdparty_registers = {
    "genset_error_0": RegisterInfo(5000, STRING(16)),
    "genset_error_1": RegisterInfo(5016, STRING(16)),
    "genset_error_2": RegisterInfo(5032, STRING(16)),
    "genset_error_3": RegisterInfo(5048, STRING(16)),
}

# Note: this is split in two to prevent hitting the pymodbus 125 register read limit (8 * 16 registers = 128)
genset_thirdparty_registers_2 = {
    "genset_error_4": RegisterInfo(5064, STRING(16)),
    "genset_error_5": RegisterInfo(5080, STRING(16)),
    "genset_error_6": RegisterInfo(5096, STRING(16)),
    "genset_error_7": RegisterInfo(5112, STRING(16)),
}


class temperature_type(Enum):
    """Temperature type."""

    BATTERY = 0
    FRIDGE = 1
    GENERIC = 2
    ROOM = 3
    OUTDOOR = 4
    WATERHEATER = 5
    FREEZER = 6


class temperature_status(Enum):
    """Temperature status."""

    OK = 0
    DISCONNECTED = 1
    SHORT_CIRCUITED = 2
    REVERSE_POLARITY = 3
    UNKNOWN = 4
    LOW_BATTERY = 5


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

temperature_registers_2 = {
    "temperature_co2": RegisterInfo(3309, UINT16, CONCENTRATION_PARTS_PER_MILLION, 1),
    "temperature_lux": RegisterInfo(3310, UINT32, LIGHT_LUX, 1),
    "temperature_nitrogen_oxides": RegisterInfo(3312, UINT16, "", 1),
    "temperature_particulate_matter": RegisterInfo(
        3313, UINT16, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER, 1
    ),
    "temperature_volatile_organic_compounds": RegisterInfo(3314, UINT16, "", 1),
}

pulsemeter_registers = {
    "pulsemeter_aggregate": RegisterInfo(3400, UINT32, UnitOfVolume.CUBIC_METERS),
    "pulsemeter_count": RegisterInfo(3402, UINT32),
}


class digitalinput_state(Enum):
    """Digital input state."""

    LOW = 0
    HIGH = 1
    OFF = 2
    ON = 3
    NO = 4
    YES = 5
    OPEN = 6
    CLOSED = 7
    ALARM = 8
    OK = 9
    RUNNING = 10
    STOPPED = 11


class digitalinput_type(Enum):
    """Digital input type."""

    DOOR = 2
    BILGE_PUMP = 3
    BILGE_ALARM = 4
    BURGLAR_ALARM = 5
    SMOKE_ALARM = 6
    FIRE_ALARM = 7
    CO2_ALARM = 8
    GENERATOR = 9


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

    STOPPED = 0
    MANUAL = 1
    TEST_RUN = 2
    LOSS_OF_COMMS = 3
    SOC = 4
    AC_LOAD = 5
    BATTERY_CURRENT = 6
    BATTERY_VOLTAGE = 7
    INVERTER_TEMPERATURE = 8
    INVERTER_OVERLOAD = 9
    STOP_ON_AC1 = 10


class generator_state(Enum):
    """Generator state."""

    STOPPED = 0
    RUNNING = 1
    WARM_UP = 2
    COOL_DOWN = 3
    STOPPING = 4
    ERROR = 10


class generator_error(Enum):
    """Generator error."""

    NONE = 0
    REMOTE_DISABLED = 1
    REMOTE_FAULT = 2


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
        3509, UINT16, entityType=SwitchWriteType()
    ),
    "generator_servicecounter": RegisterInfo(3510, UINT32, UnitOfTime.SECONDS),
    "generator_servicecounterreset": RegisterInfo(
        3512, UINT16, entityType=ButtonWriteType()
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
    "meteo_externaltemperature_sensor_2": RegisterInfo(
        3604, INT16, UnitOfTemperature.CELSIUS, 10
    ),
}
# com.victronenergy.meteo	External temperature – second sensor	3604	int16	10	-3276.8 to 3276.7	/ExternalTemperature2	no	Degrees celsius

evcharger_productid_registers = {"evcharger_productid": RegisterInfo(3800, UINT16)}


class evcharger_mode(Enum):
    """EV charger mode."""

    MANUAL = 0
    AUTO = 1
    SCHEDULED = 2


class evcharger_status(Enum):
    """EV charger status."""

    DISCONNECTED = 0
    CONNECTED = 1
    CHARGING = 2
    CHARGED = 3
    WAITING_FOR_SUN = 4
    WAITING_FOR_RFID = 5
    WAITING_FOR_START = 6
    LOW_SOC = 7
    GROUND_FAULT = 8
    WELDED_CONTACTS = 9
    CP_INPUT_SHORTED = 10
    RESIDUAL_CURRENT_DETECTED = 11
    UNDER_VOLTAGE_DETECTED = 12
    OVERVOLTAGE_DETECTED = 13
    OVERHEATING_DETECTED = 14
    CHARGING_LIMIT = 20
    START_CHARGING = 21
    SWITCHING_TO_THREE_PHASE = 22
    SWITCHING_TO_SINGLE_PHASE = 23
    STOP_CHARGING = 24

    # CODE 15 tm 19 are reserved but not yet implemented by victron


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
    "acload_frequency": RegisterInfo(3922, UINT16, UnitOfFrequency.HERTZ, 100),
}

acload_registers_1 = {
    "acload_L1_power_int32": RegisterInfo(3924, INT32, UnitOfPower.WATT),
    "acload_L2_power_int32": RegisterInfo(3926, INT32, UnitOfPower.WATT),
    "acload_L3_power_int32": RegisterInfo(3928, INT32, UnitOfPower.WATT),
    "acload_L1_powerfactor": RegisterInfo(3930, INT16, "", 1000),
    "acload_L2_powerfactor": RegisterInfo(3931, INT16, "", 1000),
    "acload_L3_powerfactor": RegisterInfo(3932, INT16, "", 1000),
    "acload_total_powerfactor": RegisterInfo(3933, INT16, "", 1000),
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

    OFF = 0
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE = 7
    POWER_SUPPLY = 11
    EXTERNAL_CONTROL = 252


class alternator_errorcode(Enum):
    """Alternator error code."""

    HIGH_BATTERY_TEMPERATURE = 12
    HIGH_BATTERY_VOLTAGE = 13
    LOW_BATTERY_VOLTAGE = 14
    VBAT_EXCEEDS_CPB = 15
    HIGH_ALTERNATOR_TEMPERATURE = 21
    ALTERNATOR_OVERSPEED = 22
    INTERNAL_ERROR = 24
    HIGH_FIELD_FET_TEMPERATURE = 41
    SENSOR_MISSING = 42
    LOW_VALT = 43
    HIGH_VOLTAGE_OFFSET = 44
    VALT_EXCEEDS_CPB = 45
    BATTERY_DISCONNECT_REQUEST = 51
    BATTERY_DISCONNECT_REQUEST_DUPLICATE_1 = 52
    BATTERY_INSTANCE_OUT_OF_RANGE = 53
    TOO_MANY_BMSES = 54
    AEBUS_FAULT = 55
    TOO_MANY_VICTRON_DEVICES = 56
    BATTERY_REQUESTED_DISCONNECTION = 58
    BATTERY_REQUESTED_DISCONNECTION_DUPLICATE_1 = 59
    BATTERY_REQUESTED_DISCONNECTION_DUPLICATE_2 = 60
    BATTERY_REQUESTED_DISCONNECTION_DUPLICATE_3 = 61
    BMS_LOST = 91
    FORCED_IDLE = 92
    DCDC_CONVERTER_FAIL = 201
    DCDC_ERROR = 202
    DCDC_ERROR_DUPLICATE_1 = 203
    DCDC_ERROR_DUPLICATE_2 = 204
    DCDC_ERROR_DUPLICATE_3 = 205
    DCDC_ERROR_DUPLICATE_4 = 206
    DCDC_ERROR_DUPLICATE_5 = 207


class alternator_mode(Enum):
    """Alternator mode."""

    ON = 1
    OFF = 4


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
    "alternator_input_voltage": RegisterInfo(
        4117, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "alternator_input_power": RegisterInfo(4118, UINT16, UnitOfPower.WATT),
    "alternator_mode": RegisterInfo(
        4119, UINT16, entityType=TextReadEntityType(alternator_mode)
    ),
    "alternator_cumulative_amp_hours_charged": RegisterInfo(
        4120,
        UINT32,
        AMPHOURS,
        10,  # note should become ah when available as data type in ha
    ),
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

    CHARGER = 1
    INVERTER = 2
    ON = 3
    OFF = 4


class multi_input_type(Enum):
    """Multi input type."""

    UNUSED = 0
    GRID = 1
    GENSET = 2
    SHORE = 3


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
    "multi_yield_user_2": RegisterInfo(4603, UINT32, UnitOfEnergy.KILO_WATT_HOUR),
    "multi_mppoperationmode_0": RegisterInfo(
        4605, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "multi_mppoperationmode_1": RegisterInfo(
        4606, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "multi_mppoperationmode_2": RegisterInfo(
        4607, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "multi_mppoperationmode_3": RegisterInfo(
        4608, UINT16, entityType=TextReadEntityType(generic_mppoperationmode)
    ),
    "multi_ess_mode": RegisterInfo(4609, UINT16, entityType=SelectWriteType(ess_mode)),
    "multi_ess_powersetpoint": RegisterInfo(
        4610, INT32, UnitOfPower.WATT, entityType=SliderWriteType("AC", True)
    ),
    "multi_disable_feed_in": RegisterInfo(4612, UINT16, entityType=SwitchWriteType()),
    "multi_disable_charge": RegisterInfo(4613, UINT16, entityType=SwitchWriteType()),
    "multi_settings_ess_minimumsoclimit": RegisterInfo(4614, UINT16, PERCENTAGE),
    "multi_sustain_active": RegisterInfo(4615, UINT16, entityType=BoolReadEntityType()),
    # RESERVED 4616 - 4619
}

multi_registers_2 = {
    "multi_alarm_shortcircuit": RegisterInfo(
        4620, UINT16, entityType=TextReadEntityType(generic_alarm_ledger)
    ),
}


class pump_state(Enum):
    """Pump state."""

    STOPPED = 0
    RUNNING = 1


class pump_mode(Enum):
    """Pump mode."""

    AUTO = 0
    ON = 1
    OFF = 2


pump_registers = {
    "pump_state": RegisterInfo(4700, UINT16, entityType=TextReadEntityType(pump_state)),
    "pump_settings_auto_start_enabled": RegisterInfo(
        4701, UINT16, entityType=SwitchWriteType()
    ),
    "pump_settings_mode": RegisterInfo(
        4702, UINT16, entityType=SelectWriteType(pump_mode)
    ),
    "pump_settings_start_value": RegisterInfo(4703, UINT16, PERCENTAGE),
    "pump_settings_stop_value": RegisterInfo(4704, UINT16, PERCENTAGE),
}


class dcdc_errorcode(Enum):
    """DCDC error codes."""

    NO_ERROR = 0
    BATTERY_TEMPERATURE_TOO_HIGH = 1
    BATTERY_VOLTAGE_TOO_HIGH = 2
    BATTERY_TEMPERATURE_SENSOR_MISWIRED_PLUS = 3
    BATTERY_TEMPERATURE_SENSOR_MISWIRED_MINUS = 4
    BATTERY_TEMPERATURE_SENSOR_DISCONNECTED = 5
    BATTERY_VOLTAGE_SENSE_MISWIRED_PLUS = 6
    BATTERY_VOLTAGE_SENSE_MISWIRED_MINUS = 7
    BATTERY_VOLTAGE_SENSE_DISCONNECTED = 8
    BATTERY_VOLTAGE_WIRE_LOSSES_TOO_HIGH = 9
    CHARGER_TEMPERATURE_TOO_HIGH = 17
    CHARGER_OVER_CURRENT = 18
    CHARGER_CURRENT_POLARITY_REVERSED = 19
    BULK_TIME_LIMIT_REACHED = 20
    CHARGER_TEMPERATURE_SENSOR_MISWIRED = 22
    CHARGER_TEMPERATURE_SENSOR_DISCONNECTED = 23
    INPUT_CURRENT_TOO_HIGH = 34


class dcdc_mode(Enum):
    """DCDC mode."""

    ON = 1
    OFF = 4


class dcdc_state(Enum):
    """DCDC state."""

    OFF = 0
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE = 7
    POWER_SUPPLY = 11


dcdc_registers = {
    "dcdc_productid": RegisterInfo(4800, UINT16),
    "dcdc_firmwareversion": RegisterInfo(4801, UINT32),
    "dcdc_errorcode": RegisterInfo(
        4803, UINT16, entityType=TextReadEntityType(dcdc_errorcode)
    ),
    "dcdc_battery_voltage": RegisterInfo(
        4804, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcdc_battery_current": RegisterInfo(4805, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "dcdc_battery_temperature": RegisterInfo(
        4806, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "dcdc_mode": RegisterInfo(4807, UINT16, entityType=SelectWriteType(dcdc_mode)),
    "dcdc_state": RegisterInfo(4808, UINT16, entityType=TextReadEntityType(dcdc_state)),
    "dcdc_input_voltage": RegisterInfo(4809, UINT16, UnitOfElectricPotential.VOLT, 100),
    "dcdc_input_power": RegisterInfo(4810, UINT16, UnitOfPower.WATT),
    "dcdc_accumulated_ah": RegisterInfo(
        4811, UINT16, AMPHOURS, 10
    ),  # Needs to be changed to ah when supported by home assistant
}


class acsystem_state(Enum):
    """AC system state."""

    OFF = 0
    LOW_POWER = 1
    FAULT = 2
    BULK = 3
    ABSORPTION = 4
    FLOAT = 5
    STORAGE = 6
    EQUALIZE = 7
    PASSTHRU = 8
    INVERTING = 9
    POWER_ASSIST = 10
    POWER_SUPPLY = 11
    EXTERNAL_CONTROL = 252


acsystem_registers = {
    "acsystem_state": RegisterInfo(
        4900, UINT16, entityType=TextReadEntityType(acsystem_state)
    ),
    "acsystem_input_L1_voltage": RegisterInfo(
        4901, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_input_L2_voltage": RegisterInfo(
        4902, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_input_L3_voltage": RegisterInfo(
        4903, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_input_L1_current": RegisterInfo(
        4904, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_input_L2_current": RegisterInfo(
        4905, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_input_L3_current": RegisterInfo(
        4906, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_input_L1_power": RegisterInfo(4907, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_input_L2_power": RegisterInfo(4908, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_input_L3_power": RegisterInfo(4909, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_input_frequency": RegisterInfo(4910, UINT16, UnitOfFrequency.HERTZ, 100),
    "acsystem_output_L1_voltage": RegisterInfo(
        4911, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_output_L2_voltage": RegisterInfo(
        4912, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_output_L3_voltage": RegisterInfo(
        4913, UINT16, UnitOfElectricPotential.VOLT, 10
    ),
    "acsystem_output_L1_current": RegisterInfo(
        4914, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_output_L2_current": RegisterInfo(
        4915, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_output_L3_current": RegisterInfo(
        4916, INT16, UnitOfElectricCurrent.AMPERE, 10
    ),
    "acsystem_output_L1_power": RegisterInfo(4917, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_output_L2_power": RegisterInfo(4918, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_output_L3_power": RegisterInfo(4919, INT16, UnitOfPower.WATT, 0.1),
    "acsystem_output_frequency": RegisterInfo(4920, UINT16, UnitOfFrequency.HERTZ, 100),
    "acsystem_ess_mode": RegisterInfo(
        4921, UINT16, entityType=SelectWriteType(ess_mode)
    ),
    "acsystem_ess_setpoint": RegisterInfo(
        4922, INT32, UnitOfPower.WATT, entityType=SliderWriteType("AC", True)
    ),
    "acsystem_disable_feed_in": RegisterInfo(
        4924, UINT16, entityType=SwitchWriteType()
    ),
    # RESERVED 4925 - 4929
}

acsystem_registers_1 = {
    "acsystem_active_soclimit": RegisterInfo(4925, UINT16, PERCENTAGE, 1),
}

acsystem_registers_2 = {
    "acsystem_alarm_gridlost": RegisterInfo(
        4930, UINT16, entityType=TextReadEntityType(generic_alarm_ledger)
    ),
    "acsystem_alarm_phaserotation": RegisterInfo(
        4931, UINT16, entityType=TextReadEntityType(generic_alarm_ledger)
    ),
    # RESERVED 4932 - 4939
}

acsystem_registers_3 = {
    "acsystem_input1_currentlimit": RegisterInfo(
        4940, UINT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", False)
    ),
    "acsystem_input2_currentlimit": RegisterInfo(
        4941, UINT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", False)
    ),
    "acsystem_gridmeter_currentlimit": RegisterInfo(
        4942, UINT16, UnitOfElectricCurrent.AMPERE, 10, SliderWriteType("AC", False)
    ),
}


dcgenset_registers = {
    "dcgenset_productid": RegisterInfo(5200, UINT16),
    "dcgenset_statuscode": RegisterInfo(5201, UINT16),
    "dcgenset_errorcode": RegisterInfo(5202, UINT16),
    "dcgenset_autostart_enabled": RegisterInfo(
        5203, UINT16, entityType=SwitchWriteType()
    ),
    "dcgenset_start": RegisterInfo(5204, UINT16, entityType=SwitchWriteType()),
    "dcgenset_dc_voltage": RegisterInfo(
        5205, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcgenset_dc_current": RegisterInfo(5206, INT16, UnitOfElectricCurrent.AMPERE, 10),
    "dcgenset_engine_load": RegisterInfo(5207, UINT16, PERCENTAGE),
    "dcgenset_engine_speed": RegisterInfo(5208, UINT16, REVOLUTIONS_PER_MINUTE),
    "dcgenset_engine_operatinghours": RegisterInfo(
        5209, UINT16, UnitOfTime.SECONDS, 0.01
    ),
    "dcgenset_engine_coolanttemperature": RegisterInfo(
        5210, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "dcgenset_engine_windingtemperature": RegisterInfo(
        5211, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "dcgenset_engine_exhausttemperature": RegisterInfo(
        5212, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "dcgenset_startervoltage": RegisterInfo(
        5213, UINT16, UnitOfElectricPotential.VOLT, 100
    ),
    "dcgenset_engine_oilpressure": RegisterInfo(5214, INT16, UnitOfPressure.KPA, 1),
    "dcgenset_heatsinktemperature": RegisterInfo(
        5215, INT16, UnitOfTemperature.CELSIUS, 10
    ),
    "dcgenset_engine_oiltemperature": RegisterInfo(
        5216, INT16, UnitOfTemperature.CELSIUS
    ),
    # RESERVED 5217
}

dcgenset_registers_thirdparty = {
    "dcgenset_error_0": RegisterInfo(5218, STRING(16)),
    "dcgenset_error_1": RegisterInfo(5234, STRING(16)),
    "dcgenset_error_2": RegisterInfo(5250, STRING(16)),
    "dcgenset_error_3": RegisterInfo(5266, STRING(16)),
}
dcgenset_registers_thirdparty_2 = {
    "dcgenset_error_4": RegisterInfo(5282, STRING(16)),
    "dcgenset_error_5": RegisterInfo(5298, STRING(16)),
    "dcgenset_error_6": RegisterInfo(5314, STRING(16)),
    "dcgenset_error_7": RegisterInfo(5330, STRING(16)),
}


class dynamic_ess_error(Enum):
    """Dynamic ESS error codes."""

    NO_ERROR = 0
    NO_ESS = 1
    ESS_MODE = 2
    NO_MATCHING_SCHEDULE = 3
    SOC_LOW = 4
    BATTERY_CAPACITY_NOT_CONFIGURED = 5


class dynamic_ess_restrictions(Enum):
    """Dynamic ESS restrictions."""

    NO_RESTRICTIONS_BETWEEN_BATTERY_AND_GRID = 0
    GRID_TO_BATTERY_RESTRICTED = 1
    BATTERY_TO_GRID_RESTRICTED = 2
    NO_ENERGY_FLOW_BETWEEN_BATTERY_AND_GRID = 3


class dynamic_ess_strategy(Enum):
    """Dynamic ESS strategy."""

    TARGET_SOC = 0
    SELF_CONSUMPTION = 1
    PRO_BATTERY = 2
    PRO_GRID = 3


system_dynamic_ess_registers = {
    "system_dynamicess_active": RegisterInfo(
        5400, UINT16, entityType=BoolReadEntityType()
    ),
    "system_dynamicess_allow_grid_feed_in": RegisterInfo(
        5401, UINT16, entityType=BoolReadEntityType()
    ),
    "system_dynamicess_available": RegisterInfo(
        5402, UINT16, entityType=BoolReadEntityType()
    ),
    "system_dynamicess_calculated_charge_rate": RegisterInfo(
        5403, UINT16, UnitOfPower.WATT, 0.1
    ),
    "system_dynamicess_error": RegisterInfo(
        5404, UINT16, entityType=TextReadEntityType(dynamic_ess_error)
    ),
    "system_dynamicess_restrictions": RegisterInfo(
        5405, UINT16, entityType=TextReadEntityType(dynamic_ess_restrictions)
    ),
    "system_dynamicess_strategy": RegisterInfo(
        5406, UINT16, entityType=TextReadEntityType(dynamic_ess_strategy)
    ),
    "system_dynamicess_targetsoc": RegisterInfo(5407, UINT16, PERCENTAGE),
}


class dynamic_ess_mode(Enum):
    """Dynamic ESS mode."""

    OFF = 0
    AUTO = 1
    NODE_RED = 4


settings_dynamic_ess_registers = {
    "settings_dynamicess_batterycapacity": RegisterInfo(
        5420, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10
    ),
    "settings_dynamicess_fullchargeduration": RegisterInfo(
        5421,
        UINT16,
        UnitOfTime.HOURS,
        entityType=SliderWriteType(powerType=UnitOfTime.HOURS),
    ),  # TODO refactor powertype to unit of importance
    "settings_dynamicess_fullchargeinterval": RegisterInfo(
        5422,
        UINT16,
        UnitOfTime.DAYS,
        entityType=SliderWriteType(powerType=UnitOfTime.DAYS),
    ),
    "settings_dynamicess_mode": RegisterInfo(
        5423, UINT16, entityType=SelectWriteType(dynamic_ess_mode)
    ),
    "settings_dynamicess_allowgridfeedin": RegisterInfo(
        5424, UINT16, entityType=SwitchWriteType()
    ),
    "settings_dynamicess_duration": RegisterInfo(
        5425, UINT16, UnitOfTime.SECONDS, entityType=SliderWriteType(UnitOfTime.SECONDS)
    ),
    "settings_dynamicess_restrictions": RegisterInfo(
        5426, UINT16, entityType=SelectWriteType(dynamic_ess_restrictions)
    ),
    "settings_dynamicess_targetsoc": RegisterInfo(
        5427, UINT16, PERCENTAGE, entityType=SliderWriteType(PERCENTAGE)
    ),
    "settings_dynamicess_schedule_starttime": RegisterInfo(
        5428, INT32, UnitOfTime.SECONDS, entityType=SliderWriteType(UnitOfTime.SECONDS)
    ),  # ,  # TODO refactor to support date and time picker and although negative is allowed this is specified as unix timestamp in the docs
    # "settings_dynamicess_strategy": RegisterInfo(
    #     5429, UINT16, entityType=SelectWriteType(dynamic_ess_strategy)
    # ),
}


class heatpump_state(Enum):
    """Heatpump state."""

    OFF = 0
    ERROR = 1
    STARTUP = 2
    HEATING = 3
    COOLING = 4


heatpump_registers = {
    "heatpump_productid": RegisterInfo(5500, UINT16),
    "heatpump_state": RegisterInfo(
        5501, UINT16, entityType=TextReadEntityType(heatpump_state)
    ),
    "heatpump_power": RegisterInfo(5502, UINT32, UnitOfPower.WATT),
    "heatpump_energy_forward": RegisterInfo(
        5504, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100
    ),
    "heatpump_temperature": RegisterInfo(5506, INT16, UnitOfTemperature.CELSIUS, 10),
    "heatpump_target_temperature": RegisterInfo(
        5507, INT16, UnitOfTemperature.CELSIUS, 10
    ),
}


class register_input_source(Enum):
    """Input source."""

    UNKNOWN = 0
    GRID = 1
    GENERATOR = 2
    SHORE = 3
    NOT_CONNECTED = 240


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

# system_internal_registers = {
#    "system_system_time_in_utc": RegisterInfo(830, UINT64, UnitOfTime.SECONDS)
# }

system_firmware_registers = {
    "system_firmware_gx_major_version": RegisterInfo(834, UINT16),
    "system_firmware_gx_beta_release": RegisterInfo(835, UINT16),
}


class system_battery_state(Enum):
    """Battery state."""

    IDLE = 0
    CHARGING = 1
    DISCHARGING = 2


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
        845, UINT16, AMPHOURS, -10
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

# Note as of 2025-01-27 the following register is marked as reserved in the documentation
# "RESERVED": RegisterInfo(867, UINT16), #com.victronenergy.system	RESERVED	867	uint16	1	0 to 65536		no

system_invertercharger_registers = {
    "system_invertercharger_current": RegisterInfo(
        868, INT32, UnitOfElectricCurrent.AMPERE, 10
    ),
    "system_invertercharger_power": RegisterInfo(870, INT32, UnitOfPower.WATT),
    "system_invertercharger_consumptiononinput_l1_power": RegisterInfo(
        872, INT32, UnitOfPower.WATT
    ),
    "system_invertercharger_consumptiononinput_l2_power": RegisterInfo(
        874, INT32, UnitOfPower.WATT
    ),
    "system_invertercharger_consumptiononinput_l3_power": RegisterInfo(
        876, INT32, UnitOfPower.WATT
    ),
    "system_invertercharger_consumptiononoutput_l1_power": RegisterInfo(
        878, INT32, UnitOfPower.WATT
    ),
    "system_invertercharger_consumptiononoutput_l2_power": RegisterInfo(
        880, INT32, UnitOfPower.WATT
    ),
    "system_invertercharger_consumptiononoutput_l3_power": RegisterInfo(
        882, INT32, UnitOfPower.WATT
    ),
}

system_pvac_registers = {
    "system_pvac_pvonoutput_L1_power": RegisterInfo(884, UINT32, UnitOfPower.WATT),
    "system_pvac_pvonoutput_L2_power": RegisterInfo(886, UINT32, UnitOfPower.WATT),
    "system_pvac_pvonoutput_L3_power": RegisterInfo(888, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongrid_L1_power": RegisterInfo(890, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongrid_L2_power": RegisterInfo(892, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongrid_L3_power": RegisterInfo(894, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongenset_L1_power": RegisterInfo(896, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongenset_L2_power": RegisterInfo(898, UINT32, UnitOfPower.WATT),
    "system_pvac_pvongenset_L3_power": RegisterInfo(900, UINT32, UnitOfPower.WATT),
}

system_power_registers_2 = {
    "system_consumption_L1_power": RegisterInfo(902, UINT32, UnitOfPower.WATT),
    "system_consumption_L2_power": RegisterInfo(904, UINT32, UnitOfPower.WATT),
    "system_consumption_L3_power": RegisterInfo(906, UINT32, UnitOfPower.WATT),
    "system_grid_L1_power": RegisterInfo(908, INT32, UnitOfPower.WATT),
    "system_grid_L2_power": RegisterInfo(910, INT32, UnitOfPower.WATT),
    "system_grid_L3_power": RegisterInfo(912, INT32, UnitOfPower.WATT),
    "system_genset_L1_power": RegisterInfo(914, INT32, UnitOfPower.WATT),
    "system_genset_L2_power": RegisterInfo(916, INT32, UnitOfPower.WATT),
    "system_genset_L3_power": RegisterInfo(918, INT32, UnitOfPower.WATT),
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
    "settings_cgwacs_registers": settings_cgwacs_registers,
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
    "genset_registers_2": genset_registers_2,
    "genset_thirdparty_registers": genset_thirdparty_registers,
    "genset_thirdparty_registers_2": genset_thirdparty_registers_2,
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
    "multi_registers_2": multi_registers_2,
    "system_registers": system_registers,
    "system_invertercharger_registers": system_invertercharger_registers,
    # "system_internal_registers": system_internal_registers,
    "system_battery_registers": system_battery_registers,
    "system_dc_registers": system_dc_registers,
    "system_charger_registers": system_charger_registers,
    "system_power_registers": system_power_registers,
    "system_bus_registers": system_bus_registers,
    "pump_registers": pump_registers,
    "dcdc_registers": dcdc_registers,
    "acsystem_registers": acsystem_registers,
    "acsystem_registers_2": acsystem_registers_2,
    "dcgenset_registers": dcgenset_registers,
    "dcgenset_registers_thirdparty": dcgenset_registers_thirdparty,
    "dcgenset_registers_thirdparty_2": dcgenset_registers_thirdparty_2,
    "system_dynamic_ess_registers": system_dynamic_ess_registers,
    "settings_dynamic_ess_registers": settings_dynamic_ess_registers,
}
