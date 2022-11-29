"""Constants for the victron integration."""
from collections import OrderedDict
from enum import Enum
#TODO change POWER_WATT and POWER_KILO_WATT to enum instead of static entry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
    POWER_KILO_WATT,
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_CURRENT_AMPERE,
    FREQUENCY_HERTZ,
    TIME_SECONDS,
    REVOLUTIONS_PER_MINUTE,
    IRRADIATION_WATTS_PER_SQUARE_METER,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfSpeed,
    UnitOfPressure
)
 
from homeassistant.components.sensor import SensorStateClass

class DeviceType(Enum):
    GRID = 1
    TANK = 2
    MULTI = 3
    VEBUS = 4


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

AC_VOLTAGES = { "US": 120, "EU": 230 } # For now only most common voltages supported
DC_VOLTAGES = { "lifepo4_12v": 12, "lifepo4_24v": 24, "lifepo4_48v": 48 } #only 3 volt nominal 4s, 8s and 16s lifepo4 configurations currently supported


class STRING():
    def __init__(self, length=1, read_length=None):
        self.length = length
        self.readLength =  read_length if read_length is not None else length*2

#maybe change to enum Enum('UINT16', 'UINT32')
UINT16 = "uint16"
INT16  = "int16"
UINT32 = "uint32"
INT32  = "int32"

class WriteType():
    def __init__(self, entityType) -> None:
        self.entityType = entityType

class SwitchWriteType(WriteType):
    def __init__(self) -> None:
        super().__init__(entityType="button")

class SliderWriteType(WriteType):
    def __init__(self, lowerLimit, upperLimit) -> None:
        super().__init__(entityType="slider")
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
    
class SelectWriteType(WriteType):
    def __init__(self, optionsEnum: Enum) -> None:
        super().__init__(entityType="select")
        self.options = optionsEnum


class RegisterInfo():
    def __init__(self, register, dataType, unit="", scale=1, writeType: WriteType = None) -> None:
        self.register = register
        self.dataType = dataType
        self.unit = unit
        self.scale = scale
        #Only used for writeable entities
        self.writeType = writeType
        
    def determine_stateclass(self):
        if self.unit == UnitOfEnergy.KILO_WATT_HOUR:
            return SensorStateClass.TOTAL_INCREASING
        elif self.unit == "":
            return None
        else:
            return SensorStateClass.MEASUREMENT



gavazi_grid_registers = { 
    "grid_L1_power": RegisterInfo(2600, INT16, UnitOfPower.WATT),
    "grid_L2_power": RegisterInfo(2601, INT16, UnitOfPower.WATT),
    "grid_L3_power": RegisterInfo(2602, INT16, UnitOfPower.WATT),
    "grid_L1_energy_forward": RegisterInfo(2603, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L3_energy_forward": RegisterInfo(2605, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L2_energy_forward": RegisterInfo(2604, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L1_energy_reverse": RegisterInfo(2606, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L2_energy_reverse": RegisterInfo(2607, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L3_energy_reverse": RegisterInfo(2608, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_serial": RegisterInfo(2609, STRING(7)),
    "grid_L1_voltage": RegisterInfo(2616, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "grid_L1_current": RegisterInfo(2617, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "grid_L2_voltage": RegisterInfo(2618, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "grid_L2_current": RegisterInfo(2619, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "grid_L3_voltage": RegisterInfo(2620, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "grid_L3_current": RegisterInfo(2621, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "grid_L1_energy_forward_total": RegisterInfo(2622, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L2_energy_forward_total": RegisterInfo(2624, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L3_energy_forward_total": RegisterInfo(2626, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L1_energy_reverse_total": RegisterInfo(2628, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L2_energy_reverse_total": RegisterInfo(2630, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_L3_energy_reverse_total": RegisterInfo(2632, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_energy_forward_total": RegisterInfo(2634, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "grid_energy_reverse_total": RegisterInfo(2636, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100)
}


vebus_registers = { 
    "vebus_activein_L1_voltage": RegisterInfo(3, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_activein_L2_voltage": RegisterInfo(4, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_activein_L3_voltage": RegisterInfo(5, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_activein_L1_current": RegisterInfo(6, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_activein_L2_current": RegisterInfo(7, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_activein_L3_current": RegisterInfo(8, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_activein_L1_frequency": RegisterInfo(9, INT16, FREQUENCY_HERTZ, 100),
    "vebus_activein_L2_frequency": RegisterInfo(10, INT16, FREQUENCY_HERTZ, 100),
    "vebus_activein_L3_frequency": RegisterInfo(11,INT16, FREQUENCY_HERTZ, 100),
    "vebus_activein_L1_power": RegisterInfo(12, INT16, UnitOfPower.WATT, 0), # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_activein_L2_power": RegisterInfo(13, INT16, UnitOfPower.WATT, 0), # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_activein_L3_power": RegisterInfo(14, INT16, UnitOfPower.WATT, 0), # could be either POWER_WATT or POWER_VOLT_AMPERE W was chosen
    "vebus_out_L1_voltage": RegisterInfo(15, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_out_L2_voltage": RegisterInfo(16, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_out_L3_voltage": RegisterInfo(17, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "vebus_out_L1_current": RegisterInfo(18, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_out_L2_current": RegisterInfo(19, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_out_L3_current": RegisterInfo(20, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_out_L1_frequency": RegisterInfo(21, INT16, FREQUENCY_HERTZ, 100),
    "vebus_activein_currentlimit": RegisterInfo(22, INT16, ELECTRIC_CURRENT_AMPERE, 10, SliderWriteType(100,100)), #TODO make this not static but user configureable
    "vebus_out_L1_power": RegisterInfo(23, INT16, UnitOfPower.WATT, 0),
    "vebus_out_L2_power": RegisterInfo(24, INT16, UnitOfPower.WATT, 0),
    "vebus_out_L3_power": RegisterInfo(25, INT16, UnitOfPower.WATT, 0),
    "vebus_battery_voltage": RegisterInfo(26, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "vebus_battery_current": RegisterInfo(27, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "vebus_numberofphases": RegisterInfo(28, UINT16), #the number count has no unit of measurement
    "vebus_activein_activeinput": RegisterInfo(29, UINT16),
    "vebus_soc": RegisterInfo(30, UINT16, PERCENTAGE, 10, SliderWriteType(0, 100)),
    "vebus_state": RegisterInfo(31, UINT16), #This has no unit of measurement
    "vebus_error": RegisterInfo(32, UINT16), #This has no unit of measurement
    "vebus_mode": RegisterInfo(33, UINT16), #This has no unit of measurement #TODO make mode selection writeable
    "vebus_alarm_hightemperature": RegisterInfo(34, UINT16), #This has no unit of measurement
    "vebus_alarm_lowbattery": RegisterInfo(35, UINT16), #This has no unit of measurement
    "vebus_alarm_overload": RegisterInfo(36, UINT16), #This has no unit of measurement
    "vebus_L1_acpowersetpoint": RegisterInfo(register=37, dataType=INT16, unit=UnitOfPower.WATT, writeType=SliderWriteType(-9000, 9000)), #TODO determine valid limits
    "vebus_disablecharge": RegisterInfo(register=38, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_disablefeedin": RegisterInfo(39, UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_L2_acpowersetpoint": RegisterInfo(register=40, dataType=INT16, unit=UnitOfPower.WATT, writeType=SliderWriteType(-9000, 9000)),
    "vebus_L3_acpowersetpoint": RegisterInfo(register=41, dataType=INT16, unit=UnitOfPower.WATT, writeType=SliderWriteType(-9000, 9000)),
    "vebus_alarm_temperaturesensor": RegisterInfo(42, UINT16), #This has no unit of measurement
    "vebus_alarm_voltagesensor": RegisterInfo(43, UINT16), #This has no unit of measurement
    "vebus_alarm_L1_higtemperature": RegisterInfo(44, UINT16), #This has no unit of measurement
    "vebus_alarm_L1_lowbattery": RegisterInfo(45, UINT16), #This has no unit of measurement
    "vebus_alarm_L1_overload": RegisterInfo(46, UINT16), #This has no unit of measurement
    "vebus_alarm_L1_ripple": RegisterInfo(47, UINT16), #This has no unit of measurement
    "vebus_alarm_L2_higtemperature": RegisterInfo(48, UINT16), #This has no unit of measurement
    "vebus_alarm_L2_lowbattery": RegisterInfo(49, UINT16), #This has no unit of measurement
    "vebus_alarm_L2_overload": RegisterInfo(50, UINT16), #This has no unit of measurement
    "vebus_alarm_L2_ripple": RegisterInfo(51, UINT16), #This has no unit of measurement
    "vebus_alarm_L3_higtemperature": RegisterInfo(52, UINT16), #This has no unit of measurement
    "vebus_alarm_L3_lowbattery": RegisterInfo(53, UINT16), #This has no unit of measurement
    "vebus_alarm_L3_overload": RegisterInfo(54, UINT16), #This has no unit of measurement
    "vebus_alarm_L3_ripple": RegisterInfo(55, UINT16), #This has no unit of measurement
    "vebus_pvinverter_disable": RegisterInfo(register=56, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_bms_allowtocharge": RegisterInfo(57, UINT16), #This has no unit of measurement
    "vebus_bms_allowtodischarge": RegisterInfo(58, UINT16), #This has no unit of measurement
    "vebus_bms_bmsexpected": RegisterInfo(59, UINT16), #This has no unit of measurement
    "vebus_bms_error": RegisterInfo(60, UINT16), #This has no unit of measurement
    "vebus_battery_temperature": RegisterInfo(61, INT16, UnitOfTemperature.CELSIUS, 10),
    "vebus_systemreset": RegisterInfo(register=62, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement # TODO use option selection here?
    "vebus_alarm_phaserotation": RegisterInfo(63, UINT16), #This has no unit of measurement
    "vebus_alarm_gridlost": RegisterInfo(64, UINT16), #This has no unit of measurement
    "vebus_donotfeedinovervoltage": RegisterInfo(register=65, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_L1_maxfeedinpower": RegisterInfo(66, UINT16, UnitOfPower.WATT, 0, SliderWriteType(-9000, 9000)),
    "vebus_L2_maxfeedinpower": RegisterInfo(67, UINT16, UnitOfPower.WATT, 0, SliderWriteType(-9000, 9000)),
    "vebus_L3_maxfeedinpower": RegisterInfo(68, UINT16, UnitOfPower.WATT, 0, SliderWriteType(-9000, 9000)),
    "vebus_state_ignoreacin1": RegisterInfo(69, UINT16), #This has no unit of measurement
    "vebus_state_ignoreacin2": RegisterInfo(70, UINT16), #This has no unit of measurement
    "vebus_targetpowerismaxfeedin": RegisterInfo(register=71, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_fixsolaroffsetto100mv": RegisterInfo(register=72, dataType=UINT16, writeType=SwitchWriteType()), #This has no unit of measurement
    "vebus_sustain": RegisterInfo(73, UINT16), #This has no unit of measurement
    "vebus_acin1toacout": RegisterInfo(74, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin1toinverter": RegisterInfo(76, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin2toacout": RegisterInfo(78, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acin2toinverter": RegisterInfo(80, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acouttoacin1": RegisterInfo(82, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_acouttoacin2": RegisterInfo(84, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacin1": RegisterInfo(86, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacin2": RegisterInfo(88, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_invertertoacout": RegisterInfo(90, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "vebus_outtoinverter": RegisterInfo(92, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100)
}

battery_registers = {
    "battery_voltage": RegisterInfo(259, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_starter_voltage": RegisterInfo(260, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_current": RegisterInfo(261, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "battery_temperature": RegisterInfo(262, INT16, UnitOfTemperature.CELSIUS, 10),
    "battery_midvoltage": RegisterInfo(263, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_midvoltagedeviation": RegisterInfo(264, UINT16, PERCENTAGE, 100),
    "battery_consumedamphours": RegisterInfo(265, UINT16, ELECTRIC_CURRENT_AMPERE, -10),
    "battery_soc": RegisterInfo(266, UINT16, PERCENTAGE, 10),
    "battery_alarm": RegisterInfo(267, UINT16),
    "battery_alarm_lowvoltage": RegisterInfo(268, UINT16),
    "battery_alarm_highvoltage": RegisterInfo(269, UINT16),
    "battery_alarm_lowstartervoltage": RegisterInfo(270, UINT16),
    "battery_alarm_highstartervoltage": RegisterInfo(271, UINT16),
    "battery_alarm_lowsoc": RegisterInfo(272, UINT16),
    "battery_alarm_lowtemperature": RegisterInfo(273, UINT16),
    "battery_alarm_hightemperature": RegisterInfo(274, UINT16),
    "battery_alarm_midvoltage": RegisterInfo(275, UINT16),
    "battery_alarm_lowfusedvoltage": RegisterInfo(276, UINT16),
    "battery_alarm_highfusedvoltage": RegisterInfo(277, UINT16),
    "battery_alarm_fuseblown": RegisterInfo(278, UINT16),
    "battery_alarm_highinternaltemperature": RegisterInfo(279, UINT16),
    "battery_relay": RegisterInfo(register=280, dataType=UINT16, writeType=SwitchWriteType()),
    "battery_history_deepestdischarge": RegisterInfo(281, UINT16, ELECTRIC_CURRENT_AMPERE, -10),
    "battery_history_lastdischarge": RegisterInfo(282, UINT16, ELECTRIC_CURRENT_AMPERE, -10),
    "battery_history_averagedischarge": RegisterInfo(283, UINT16, ELECTRIC_CURRENT_AMPERE, -10),
    "battery_history_chargecycles": RegisterInfo(284, UINT16),
    "battery_history_fulldischarges": RegisterInfo(285, UINT16),
    "battery_history_totalahdrawn": RegisterInfo(286, UINT16, ELECTRIC_CURRENT_AMPERE, -10),
    "battery_history_minimumvoltage": RegisterInfo(287, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_maximumvoltage": RegisterInfo(288, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_timesincelastfullcharge": RegisterInfo(289, UINT16, TIME_SECONDS, 0),
    "battery_history_automaticsyncs": RegisterInfo(290, UINT16),
    "battery_history_lowvoltagealarms": RegisterInfo(291, UINT16),
    "battery_history_highvoltagealarms": RegisterInfo(292, UINT16),
    "battery_history_lowstartervoltagealarms": RegisterInfo(293, UINT16),
    "battery_history_highstartervoltagealarms": RegisterInfo(294, UINT16),
    "battery_history_minimumstartervoltage": RegisterInfo(295, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_maximumstartervoltage": RegisterInfo(296, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_lowfusedvoltagealarms": RegisterInfo(297, UINT16),
    "battery_history_highfusedvoltagealarms": RegisterInfo(298, UINT16),
    "battery_history_minimumfusedvoltage": RegisterInfo(299, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_maximumfusedvoltage": RegisterInfo(300, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_dischargedenergy": RegisterInfo(301, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "battery_history_chargedenergy": RegisterInfo(302, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "battery_timetogo": RegisterInfo(303, UINT16, TIME_SECONDS, 0),
    "battery_soh": RegisterInfo(304, UINT16, PERCENTAGE, 10),
    "battery_info_maxchargevoltage": RegisterInfo(305, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "battery_info_batterylowvoltage": RegisterInfo(306, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "battery_info_maxchargecurrent": RegisterInfo(307, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "battery_info_maxdischargecurrent": RegisterInfo(308, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "battery_capacity": RegisterInfo(309, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "battery_diagnostics_lasterror_1_time": RegisterInfo(310, INT32, "timestamp" ,1), #todo check if decimal scale value is used here # extract timestamp
    "battery_diagnostics_lasterror_2_time": RegisterInfo(312, INT32, "timestamp" ,1), #todo check if decimal scale value is used here # extract timestamp
    "battery_diagnostics_lasterror_3_time": RegisterInfo(314, INT32, "timestamp" ,1), #todo check if decimal scale value is used here # extract timestamp
    "battery_diagnostics_lasterror_4_time": RegisterInfo(316, INT32, "timestamp" ,1), #todo check if decimal scale value is used here # extract timestamp
    "battery_system_mincelltemperature": RegisterInfo(318, INT16, UnitOfTemperature.CELSIUS, 10),
    "battery_system_maxcelltemperature": RegisterInfo(319, INT16, UnitOfTemperature.CELSIUS, 10),
    "battery_alarm_higchargecurrent": RegisterInfo(320, UINT16),
    "battery_alarm_highdischargecurrent": RegisterInfo(321, UINT16),
    "battery_alarm_cellimbalance": RegisterInfo(322, UINT16),
    "battery_alarm_internalfailure": RegisterInfo(323, UINT16),
    "battery_alarm_highchargetemperature": RegisterInfo(324, UINT16),
    "battery_alarm_lowchargetemperature": RegisterInfo(325, UINT16),
    "battery_alarm_lowcellvoltage": RegisterInfo(326, UINT16)
}

battery_detail_registers = {
    "battery_state": RegisterInfo(1282, UINT16),
    "battery_error": RegisterInfo(1283, UINT16),
    "battery_system_switch": RegisterInfo(1284, UINT16),
    "battery_balancing": RegisterInfo(1285, UINT16),
    "battery_system_numberofbatteries": RegisterInfo(1286, UINT16),
    "battery_system_batteriesparallel": RegisterInfo(1287, UINT16),
    "battery_system_batteriesseries": RegisterInfo(1288, UINT16),
    "battery_system_numberofcellsperbattery": RegisterInfo(1289, UINT16),
    "battery_system_mincellvoltage": RegisterInfo(1290, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_system_maxcellvoltage": RegisterInfo(1291, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_diagnostics_shutdownsdueerror": RegisterInfo(1292, UINT16),
    "battery_diagnostics_lasterror_1": RegisterInfo(1293, UINT16),
    "battery_diagnostics_lasterror_2": RegisterInfo(1294, UINT16),
    "battery_diagnostics_lasterror_3": RegisterInfo(1295, UINT16),
    "battery_diagnostics_lasterror_4": RegisterInfo(1296, UINT16),
    "battery_io_allowtocharge": RegisterInfo(1297, UINT16),
    "battery_io_allowtodischarge": RegisterInfo(1298, UINT16),
    "battery_io_externalrelay": RegisterInfo(1299, UINT16),
    "battery_history_minimumcellvoltage": RegisterInfo(1300, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_history_maximumcellvoltage": RegisterInfo(1301, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "battery_system_numberofmodulesoffline": RegisterInfo(1302, UINT16),
    "battery_system_numberofmodulesonline": RegisterInfo(1303, UINT16),
    "battery_system_numberofmodulesblockingcharge": RegisterInfo(1304, UINT16),
    "battery_system_numberofmodulesblockingdischarge": RegisterInfo(1305, UINT16),
    "battery_system_minvoltagecellid": RegisterInfo(1306, STRING(4)),
    "battery_system_maxvoltagecellid": RegisterInfo(1310, STRING(4)),
    "battery_system_mintemperaturecellid": RegisterInfo(1314, STRING(4)),
    "battery_system_maxtemperaturecellid": RegisterInfo(1318, STRING(4))
}

solarcharger_registers = {
    "solarcharger_battery_voltage": RegisterInfo(771, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "solarcharger_battery_current": RegisterInfo(772, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "solarcharger_battery_temperature": RegisterInfo(773, INT16, UnitOfTemperature.CELSIUS, 10),
    "solarcharger_mode": RegisterInfo(774, UINT16), #TODO setup enum selection option for mode
    "solarcharger_state": RegisterInfo(775, UINT16),
    "solarcharger_pv_voltage": RegisterInfo(776, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "solarcharger_pv_current": RegisterInfo(777, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "solarcharger_equallization_pending": RegisterInfo(778, UINT16),
    "solarcharger_equalization_time_remaining": RegisterInfo(779, UINT16, TIME_SECONDS, 10),
    "solarcharger_relay": RegisterInfo(780, UINT16),
    "solarcharger_alarm": RegisterInfo(781, UINT16),
    "solarcharger_alarm_lowvoltage": RegisterInfo(782, UINT16),
    "solarcharger_alarm_highvoltage": RegisterInfo(783, UINT16),
    "solarcharger_yield_today": RegisterInfo(784, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_maxpower_today": RegisterInfo(785, UINT16, UnitOfPower.WATT),
    "solarcharger_yield_yesterday": RegisterInfo(786, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_maxpower_yesterday": RegisterInfo(787, UINT16, UnitOfPower.WATT),
    "solarcharger_errorcode": RegisterInfo(788, UINT16),
    "solarcharger_yield_power": RegisterInfo(789, UINT16, UnitOfPower.WATT, 10),
    "solarcharger_yield_user": RegisterInfo(790, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_mppoperationmode": RegisterInfo(791, UINT16)
}

solarcharger_tracker_voltage_registers = {
    "solarcharger_tracker_0_voltage": RegisterInfo(3700, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "solarcharger_tracker_1_voltage": RegisterInfo(3701, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "solarcharger_tracker_2_voltage": RegisterInfo(3702, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "solarcharger_tracker_3_voltage": RegisterInfo(3703, UINT16, ELECTRIC_POTENTIAL_VOLT, 100)
}
#TODO check if this register gap can be read skipped.
solarcharger_tracker_registers = {
    "solarcharger_tracker_0_yield_today": RegisterInfo(3708, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_1_yield_today": RegisterInfo(3709, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_2_yield_today": RegisterInfo(3710, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_3_yield_today": RegisterInfo(3711, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_0_yield_yesterday": RegisterInfo(3712, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_1_yield_yesterday": RegisterInfo(3713, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_2_yield_yesterday": RegisterInfo(3714, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_3_yield_yesterday": RegisterInfo(3715, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "solarcharger_tracker_0_maxpower_today": RegisterInfo(3716, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_1_maxpower_today": RegisterInfo(3717, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_2_maxpower_today": RegisterInfo(3718, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_3_maxpower_today": RegisterInfo(3719, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_0_maxpower_yesterday": RegisterInfo(3720, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_1_maxpower_yesterday": RegisterInfo(3721, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_2_maxpower_yesterday": RegisterInfo(3722, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_3_maxpower_yesterday": RegisterInfo(3723, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_0_pv_power": RegisterInfo(3724, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_1_pv_power": RegisterInfo(3725, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_2_pv_power": RegisterInfo(3726, UINT16, UnitOfPower.WATT),
    "solarcharger_tracker_3_pv_power": RegisterInfo(3727, UINT16, UnitOfPower.WATT),    
}

pvinverter_registers = {
    "pvinverter_position": RegisterInfo(1026, UINT16),
    "pvinverter_L1_voltage": RegisterInfo(1027, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "pvinverter_L1_current": RegisterInfo(1028, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "pvinverter_L1_power": RegisterInfo(1029, UINT16, UnitOfPower.WATT),
    "pvinverter_L1_energy_forward": RegisterInfo(1030, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_L2_voltage": RegisterInfo(1031, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "pvinverter_L2_current": RegisterInfo(1032, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "pvinverter_L2_power": RegisterInfo(1033, UINT16, UnitOfPower.WATT),
    "pvinverter_L2_energy_forward": RegisterInfo(1034, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_L3_voltage": RegisterInfo(1035, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "pvinverter_L3_current": RegisterInfo(1036, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "pvinverter_L3_power": RegisterInfo(1037, UINT16, UnitOfPower.WATT),
    "pvinverter_L3_energy_forward": RegisterInfo(1038, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_serial": RegisterInfo(1039, STRING(7)),
    "pvinverter_L1_energy_forward_total": RegisterInfo(1046, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_L2_energy_forward_total": RegisterInfo(1048, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_L3_energy_forward_total": RegisterInfo(1050, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "pvinverter_power_total": RegisterInfo(1052, INT32, POWER_KILO_WATT),
    "pvinverter_power_max_capacity": RegisterInfo(1054, UINT32, POWER_KILO_WATT),
    "pvinverter_powerlimit": RegisterInfo(register=1056, dataType=UINT32, unit=UnitOfPower.WATT, writeType=SliderWriteType(0, 9000))  #TODO determine min max based on user config
}

motordrive_registers = {
    "motordrive_rpm": RegisterInfo(2048, INT16, REVOLUTIONS_PER_MINUTE),
    "motordrive_motor_temperature": RegisterInfo(2049, INT16, UnitOfTemperature.CELSIUS, 10),
    "motordrive_voltage": RegisterInfo(2050, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "motordrive_current": RegisterInfo(2051, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "motordrive_power": RegisterInfo(2052, INT16, UnitOfPower.WATT, 10),
    "motordrive_controller_temperature": RegisterInfo(2053, INT16, UnitOfTemperature.CELSIUS, 10)
}

charger_registers = {
    "charger_voltage_output_1": RegisterInfo(2307, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "charger_current_output_1": RegisterInfo(2308, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "charger_temperature": RegisterInfo(2309, INT16, UnitOfTemperature.CELSIUS, 10),
    "charger_voltage_output_2": RegisterInfo(2310, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "charger_current_output_2": RegisterInfo(2311, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "charger_voltage_output_3": RegisterInfo(2312, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "charger_current_output_3": RegisterInfo(2313, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "charger_L1_current": RegisterInfo(2314, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "charger_L1_power": RegisterInfo(2315, UINT16, UnitOfPower.WATT),
    "charger_current_limit": RegisterInfo(2316, INT16, ELECTRIC_CURRENT_AMPERE, 10, writeType=SliderWriteType(-100, 100)), #TODO make user configureable
    "charger_mode": RegisterInfo(2317, UINT16), #TODO support charger mode enum
    "charger_state": RegisterInfo(2318, UINT16),
    "charger_errorcode": RegisterInfo(2319, UINT16),
    "charger_relay": RegisterInfo(2320, UINT16),
    "charger_alarm_lowvoltage": RegisterInfo(2321, UINT16),
    "charger_alarm_highvoltage": RegisterInfo(2322, UINT16)
}

settings_registers = {
    "settings_ess_acpowersetpoint": RegisterInfo(register=2700, dataType=INT16, unit=UnitOfPower.WATT, writeType=SliderWriteType(-9000, 9000)), #TODO make user configureable
    "settings_ess_maxchargepercentage": RegisterInfo(register=2701, dataType=UINT16, unit=PERCENTAGE, writeType=SliderWriteType(0, 100)),
    "settings_ess_maxdischargepercentage": RegisterInfo(register=2702, dataType=UINT16, unit=PERCENTAGE, writeType=SliderWriteType(0, 100)),
    "settings_ess_acpowersetpoint2": RegisterInfo(2703, INT16, UnitOfPower.WATT, 0, SliderWriteType(-9000, 9000)), # Duplicate register exposed by victron #TODO make user configureable
    "settings_ess_maxdischargepower": RegisterInfo(2704, UINT16, UnitOfPower.WATT, 0, SliderWriteType(0, 9000)), #TODO make user configureable
    "settings_ess_maxchargecurrent": RegisterInfo(register=2705, dataType=INT16, unit=ELECTRIC_CURRENT_AMPERE, writeType=SliderWriteType(-100, 100)), #TODO make user configureable
    "settings_ess_maxfeedinpower": RegisterInfo(2706, INT16, UnitOfPower.WATT, 0, SliderWriteType(-9000, 9000)), #TODO make user configureable
    "settings_ess_overvoltagefeedin": RegisterInfo(register=2707, dataType=INT16, writeType=SwitchWriteType()),
    "settings_ess_preventfeedback": RegisterInfo(register=2708, dataType=INT16, writeType=SwitchWriteType()),
    "settings_ess_feedinpowerlimit": RegisterInfo(2709, INT16), #TODO introduce binary sensor here?
    "settings_systemsetup_maxchargevoltage": RegisterInfo(2710, UINT16, ELECTRIC_POTENTIAL_VOLT, 10, SliderWriteType(0, 60)) #TODO make user configureable
}

gps_registers = {
    "gps_latitude": RegisterInfo(2800, INT32, "", 10000000),
    "gps_longitude": RegisterInfo(2802, INT32, "", 10000000),
    "gps_course": RegisterInfo(2804, UINT16, "", 100),
    "gps_speed": RegisterInfo(2805, UINT16, UnitOfSpeed.METERS_PER_SECOND, 100),
    "gps_fix": RegisterInfo(2806, UINT16),
    "gps_numberofsatellites": RegisterInfo(2807, UINT16),
    "gps_altitude": RegisterInfo(2808, INT32, UnitOfSpeed.METERS_PER_SECOND, 10)
}

settings_ess_registers = {
    "settings_ess_batterylife_state": RegisterInfo(2900, UINT16), #TODO introduce enum for selection writetype
    "settings_ess_batterylife_minimumsoc": RegisterInfo(2901, UINT16, PERCENTAGE, 10, SliderWriteType(0, 100)), #TODO make user configureable
    "settings_ess_mode": RegisterInfo(2902, UINT16), #TODO introduce enum for mode selection
    "settings_ess_batterylife_soclimit": RegisterInfo(2903, UINT16, PERCENTAGE, 10), #TODO not writeable

}

tank_registers = {
    "tank_productid": RegisterInfo(3000, UINT16),
    "tank_capacity": RegisterInfo(3001, UINT32, UnitOfVolume.CUBIC_METERS, 10000),
    "tank_fluidtype": RegisterInfo(3003, UINT16),
    "tank_level": RegisterInfo(3004, UINT16, PERCENTAGE, 10),
    "tank_remaining": RegisterInfo(3005, UINT32, UnitOfVolume.CUBIC_METERS, 10000),
    "tank_status": RegisterInfo(3007, UINT16)
}

inverter_output_registers = {
    "inverter_output_L1_current": RegisterInfo(3100, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "inverter_output_L1_voltage": RegisterInfo(3101, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "inverter_output_L1_power": RegisterInfo(3102, INT16, UnitOfPower.WATT, 0),
}

inverter_battery_registers = {
    "inverter_battery_voltage": RegisterInfo(3105, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "inverter_battery_current": RegisterInfo(3106, INT16, ELECTRIC_CURRENT_AMPERE, 10),
}

inverter_alarm_registers = {
    "inverter_alarm_hightemperature": RegisterInfo(3110, UINT16),
    "inverter_alarm_highbatteryvoltage": RegisterInfo(3111, UINT16),
    "inverter_alarm_highacoutvoltage": RegisterInfo(3112, UINT16),
    "inverter_alarm_lowtemperature": RegisterInfo(3113, UINT16),
    "inverter_alarm_lowbatteryvoltage": RegisterInfo(3114, UINT16),
    "inverter_alarm_lowacoutvoltage": RegisterInfo(3115, UINT16),
    "inverter_alarm_overload": RegisterInfo(3116, UINT16),
    "inverter_alarm_ripple": RegisterInfo(3117, UINT16),
}

inverter_info_registers = {
    "inverter_info_firmwareversion": RegisterInfo(3125, UINT16),
    "inverter_info_mode": RegisterInfo(3126, UINT16), #TODO introduce selection mode enum
    "inverter_info_productid": RegisterInfo(3127, UINT16),
    "inverter_info_state": RegisterInfo(3128, UINT16),
}

#PV voltage is present here due to poor register id selection by victron
inverter_energy_registers = {
    "inverter_energy_invertertoacout": RegisterInfo(3130, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "inverter_energy_outtoinverter": RegisterInfo(3132, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "inverter_energy_solartoacout": RegisterInfo(3134, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "inverter_energy_solartobattery": RegisterInfo(3136, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "inverter_pv_voltage_single_tracker": RegisterInfo(3138, UINT16, ELECTRIC_POTENTIAL_VOLT, 10)
}

inverter_tracker_registers = {
    "inverter_tracker_0_voltage": RegisterInfo(3140, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "inverter_tracker_1_voltage": RegisterInfo(3141, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "inverter_tracker_2_voltage": RegisterInfo(3142, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "inverter_tracker_3_voltage": RegisterInfo(3143, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
}

inverter_tracker_statistics_registers = {
    "inverter_tracker_0_yield_today": RegisterInfo(3148, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_1_yield_today": RegisterInfo(3149, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_2_yield_today": RegisterInfo(3150, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_3_yield_today": RegisterInfo(3151, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_0_yield_yesterday": RegisterInfo(3152, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_1_yield_yesterday": RegisterInfo(3153, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_2_yield_yesterday": RegisterInfo(3154, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_3_yield_yesterday": RegisterInfo(3155, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "inverter_tracker_0_maxpower_today": RegisterInfo(3156, UINT16, UnitOfPower.WATT),
    "inverter_tracker_1_maxpower_today": RegisterInfo(3157, UINT16, UnitOfPower.WATT),
    "inverter_tracker_2_maxpower_today": RegisterInfo(3158, UINT16, UnitOfPower.WATT),
    "inverter_tracker_3_maxpower_today": RegisterInfo(3159, UINT16, UnitOfPower.WATT),    
    "inverter_tracker_0_maxpower_yesterday": RegisterInfo(3160, UINT16, UnitOfPower.WATT),
    "inverter_tracker_1_maxpower_yesterday": RegisterInfo(3161, UINT16, UnitOfPower.WATT),
    "inverter_tracker_2_maxpower_yesterday": RegisterInfo(3162, UINT16, UnitOfPower.WATT),
    "inverter_tracker_3_maxpower_yesterday": RegisterInfo(3163, UINT16, UnitOfPower.WATT),
    "inverter_tracker_0_power": RegisterInfo(3164, UINT16, UnitOfPower.WATT),
    "inverter_tracker_1_power": RegisterInfo(3165, UINT16, UnitOfPower.WATT),
    "inverter_tracker_2_power": RegisterInfo(3166, UINT16, UnitOfPower.WATT),
    "inverter_tracker_3_power": RegisterInfo(3167, UINT16, UnitOfPower.WATT),
    "inverter_alarm_lowsoc": RegisterInfo(3168, UINT16)
}

genset_registers = {
    "genset_L1_voltage": RegisterInfo(3200, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "genset_L2_voltage": RegisterInfo(3201, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "genset_L3_voltage": RegisterInfo(3202, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "genset_L1_current": RegisterInfo(3203, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "genset_L2_current": RegisterInfo(3204, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "genset_L3_current": RegisterInfo(3205, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "genset_L1_power": RegisterInfo(3206, INT16, UnitOfPower.WATT),
    "genset_L2_power": RegisterInfo(3207, INT16, UnitOfPower.WATT),
    "genset_L3_power": RegisterInfo(3208, INT16, UnitOfPower.WATT),
    "genset_L1_frequency": RegisterInfo(3209, UINT16, FREQUENCY_HERTZ, 100),
    "genset_L2_frequency": RegisterInfo(3210, UINT16, FREQUENCY_HERTZ, 100),
    "genset_L3_frequency": RegisterInfo(3211, UINT16, FREQUENCY_HERTZ, 100),
    "genset_productid": RegisterInfo(3212, UINT16),
    "genset_statuscode": RegisterInfo(3213, UINT16),
    "genset_errorcode": RegisterInfo(3214, UINT16),
    "genset_autostart": RegisterInfo(3215, UINT16),
    "genset_engine_load": RegisterInfo(3216, UINT16, PERCENTAGE),
    "genset_engine_speed": RegisterInfo(3217, UINT16, REVOLUTIONS_PER_MINUTE),
    "genset_engine_operatinghours": RegisterInfo(3218, UINT16, TIME_SECONDS, 0),
    "genset_engine_coolanttemperature": RegisterInfo(3219, INT16, UnitOfTemperature.CELSIUS, 10),
    "genset_engine_windingtemperature": RegisterInfo(3220, INT16, UnitOfTemperature.CELSIUS, 10),
    "genset_engine_exhausttemperature": RegisterInfo(3221, INT16, UnitOfTemperature.CELSIUS, 10),
    "genset_startervoltage": RegisterInfo(3222, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "genset_start": RegisterInfo(register=3223, dataType=UINT16, writeType=SwitchWriteType())
}

temperature_registers = {
    "temperature_productid": RegisterInfo(3300, UINT16),
    "temperature_scale": RegisterInfo(3301, UINT16, "", 100),
    "temperature_offset": RegisterInfo(3302, INT16, "",100),
    "temperature_type": RegisterInfo(3303, UINT16),
    "temperature_temperature": RegisterInfo(3304, INT16, UnitOfTemperature.CELSIUS, 100),
    "temperature_status": RegisterInfo(3305, UINT16),
    "temperature_humidity": RegisterInfo(3306, UINT16, PERCENTAGE, 10),
    "temperature_batteryvoltage": RegisterInfo(3307, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "temperature_pressure": RegisterInfo(3308, UINT16, UnitOfPressure.HPA)
}

pulsemeter_registers = {
    "pulsemeter_aggregate": RegisterInfo(3400, UINT32, UnitOfVolume.CUBIC_METERS),
    "pulsemeter_count": RegisterInfo(3402, UINT32)
}

digitalinput_registers = {
    "digitalinput_count": RegisterInfo(3420, UINT32),
    "digitalinput_state": RegisterInfo(3422, UINT16),
    "digitalinput_alarm": RegisterInfo(3423, UINT16),
    "digitalinput_type": RegisterInfo(3424, UINT16)
}

generator_registers = {
    "generator_manualstart": RegisterInfo(register=3500, dataType=UINT16, writeType=SwitchWriteType()), #TODO check setting inversion for value interpretation
    "generator_runningbyconditioncode": RegisterInfo(3501, UINT16),
    "generator_runtime": RegisterInfo(3502, UINT16, TIME_SECONDS, 0), #documentation says 1 scale. assuming this is incorrect and 0 should be used like all other seconds registers
    "generator_quiethours": RegisterInfo(3503, UINT16),
    "generator_runtime_2": RegisterInfo(3504, UINT32, TIME_SECONDS, 0),
    "generator_state": RegisterInfo(3506, UINT16),
    "generator_error": RegisterInfo(3507, UINT16),
    "generator_alarm_nogeneratoratacin": RegisterInfo(3508, UINT16),
    "generator_autostartenabled": RegisterInfo(register=3509, dataType=UINT16, writeType=SwitchWriteType())
}

#not processed yet
meteo_registers = {
    "meteo_irradiance": RegisterInfo(3600, UINT16, IRRADIATION_WATTS_PER_SQUARE_METER, 10),
    "meteo_windspeed": RegisterInfo(3601, UINT16, UnitOfSpeed.METERS_PER_SECOND, 10),
    "meteo_celltemperature": RegisterInfo(3602, INT16, UnitOfTemperature.CELSIUS, 10),
    "meteo_externaltemperature": RegisterInfo(3603, INT16, UnitOfTemperature.CELSIUS, 10)
}

evcharger_productid_registers = {
    "evcharger_productid": RegisterInfo(3800, UINT16)
}

evcharger_registers = {
    "evcharger_firmwareversion": RegisterInfo(3802, UINT32),
    "evcharger_serial": RegisterInfo(3804, STRING(6)),
    "evcharger_model": RegisterInfo(3810, STRING(4)),
    "evcharger_maxcurrent": RegisterInfo(register=3814, dataType=UINT16, unit=ELECTRIC_CURRENT_AMPERE, writeType=SliderWriteType(0, 100)), #TODO make user configureable
    "evcharger_mode": RegisterInfo(3815, UINT16),#TODO introduce mode enums
    "evcharger_energy_forward": RegisterInfo(3816, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "evcharger_L1_power": RegisterInfo(3818, UINT16, UnitOfPower.WATT),
    "evcharger_L2_power": RegisterInfo(3819, UINT16, UnitOfPower.WATT),
    "evcharger_L3_power": RegisterInfo(3820, UINT16, UnitOfPower.WATT),
    "evcharger_total_power": RegisterInfo(3821, UINT16, UnitOfPower.WATT),
    "evcharger_chargingtime": RegisterInfo(3822, UINT16, TIME_SECONDS, 0),
    "evcharger_current": RegisterInfo(3823, UINT16, ELECTRIC_CURRENT_AMPERE),
    "evcharger_status": RegisterInfo(3824, UINT16),
    "evcharger_setcurrent": RegisterInfo(register=3825, dataType=UINT16, unit=ELECTRIC_CURRENT_AMPERE, writeType=SliderWriteType(0, 100)), #TODO make user configureable
    "evcharger_startstop": RegisterInfo(register=3826, dataType=UINT16, writeType=SwitchWriteType()),
    "evcharger_position": RegisterInfo(3827, UINT16), #TODO introduce position enums

}

acload_registers = {
    "acload_L1_power": RegisterInfo(3900, UINT16, UnitOfPower.WATT),
    "acload_L2_power": RegisterInfo(3901, UINT16, UnitOfPower.WATT),
    "acload_L3_power": RegisterInfo(3902, UINT16, UnitOfPower.WATT),
    "acload_serial": RegisterInfo(3903, STRING(7)),
    "acload_L1_voltage": RegisterInfo(3910, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "acload_L1_current": RegisterInfo(3911, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "acload_L2_voltage": RegisterInfo(3912, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "acload_L2_current": RegisterInfo(3913, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "acload_L3_voltage": RegisterInfo(3914, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "acload_L3_current": RegisterInfo(3915, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "acload_L1_energy_forward": RegisterInfo(3916, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "acload_L2_energy_forward": RegisterInfo(3918, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "acload_L3_energy_forward": RegisterInfo(3920, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100)
}

fuelcell_registers = {
    "fuelcell_battery_voltage": RegisterInfo(4000, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "fuelcell_battery_current": RegisterInfo(4001, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "fuelcell_starter_voltage": RegisterInfo(4002, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "fuelcell_temperature": RegisterInfo(4003, INT16, UnitOfTemperature.CELSIUS, 10),
    "fuelcell_history_energyout": RegisterInfo(4004, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "fuelcell_alarm_lowvoltage": RegisterInfo(4006, UINT16),
    "fuelcell_alarm_highvoltage": RegisterInfo(4007, UINT16),
    "fuelcell_alarm_lowstartervoltage": RegisterInfo(4008, UINT16),
    "fuelcell_alarm_highstartervoltage": RegisterInfo(4009, UINT16),
    "fuelcell_alarm_lowtemperature": RegisterInfo(4010, UINT16),
    "fuelcell_alarm_hightemperature": RegisterInfo(4011, UINT16)
}

alternator_registers = {
    "alternator_battery_voltage": RegisterInfo(4100, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "alternator_battery_current": RegisterInfo(4101, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "alternator_startervoltage": RegisterInfo(4102, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "alternator_temperature": RegisterInfo(4103, INT16, UnitOfTemperature.CELSIUS, 10),
    "alternator_history_energyout": RegisterInfo(4104, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "alternator_alarm_lowvoltage": RegisterInfo(4106, UINT16),
    "alternator_alarm_highvoltage": RegisterInfo(4107, UINT16),
    "alternator_alarm_lowstartervoltage": RegisterInfo(4108, UINT16),
    "alternator_alarm_highstartervoltage": RegisterInfo(4109, UINT16),
    "alternator_alarm_lowtemperature": RegisterInfo(4110, UINT16),
    "alternator_alarm_hightemperature": RegisterInfo(4111, UINT16),
    "alternator_state": RegisterInfo(4112, UINT16),
    "alternator_errorcode": RegisterInfo(4113, UINT16),
    "alternator_engine_speed": RegisterInfo(4114, UINT16, REVOLUTIONS_PER_MINUTE),
    "alternator_alternator_speed": RegisterInfo(4115, UINT16, REVOLUTIONS_PER_MINUTE),
    "alternator_fielddrive": RegisterInfo(4116, UINT16, PERCENTAGE)
}

dcsource_registers = {
    "dcsource_battery_voltage": RegisterInfo(4200, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcsource_battery_current": RegisterInfo(4201, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "dcsource_starter_voltage": RegisterInfo(4202, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcsource_temperature": RegisterInfo(4203, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcsource_history_energyout": RegisterInfo(4204, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "dcsource_alarm_lowvoltage": RegisterInfo(4206, UINT16),
    "dcsource_alarm_highvoltage": RegisterInfo(4207, UINT16),
    "dcsource_alarm_lowstartervoltage": RegisterInfo(4208, UINT16),
    "dcsource_alarm_highstartervoltage": RegisterInfo(4209, UINT16),
    "dcsource_alarm_lowtemperature": RegisterInfo(4210, UINT16),
    "dcsource_alarm_hightemperature": RegisterInfo(4211, UINT16),
}

dcload_registers = {
    "dcload_battery_voltage": RegisterInfo(4300, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcload_battery_current": RegisterInfo(4301, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "dcload_starter_voltage": RegisterInfo(4302, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcload_temperature": RegisterInfo(4303, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcload_history_energyin": RegisterInfo(4304, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "dcload_alarm_lowvoltage": RegisterInfo(4306, UINT16),
    "dcload_alarm_highvoltage": RegisterInfo(4307, UINT16),
    "dcload_alarm_lowstartervoltage": RegisterInfo(4308, UINT16),
    "dcload_alarm_highstartervoltage": RegisterInfo(4309, UINT16),
    "dcload_alarm_lowtemperature": RegisterInfo(4310, UINT16),
    "dcload_alarm_hightemperature": RegisterInfo(4311, UINT16)
}

dcsystem_registers = {
    "dcsystem_battery_voltage": RegisterInfo(4400, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcsystem_battery_current": RegisterInfo(4401, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "dcsystem_starter_voltage": RegisterInfo(4402, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "dcsystem_temperature": RegisterInfo(4403, INT16, UnitOfTemperature.CELSIUS, 10),
    "dcsystem_history_energyout": RegisterInfo(4404, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "dcsystem_history_energyin": RegisterInfo(4406, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "dcsystem_alarm_lowvoltage": RegisterInfo(4408, UINT16),
    "dcsystem_alarm_highvoltage": RegisterInfo(4409, UINT16),
    "dcsystem_alarm_lowstartervoltage": RegisterInfo(4410, UINT16),
    "dcsystem_alarm_highstartervoltage": RegisterInfo(4411, UINT16),
    "dcsystem_alarm_lowtemperature": RegisterInfo(4412, UINT16),
    "dcsystem_alarm_hightemperature": RegisterInfo(4413, UINT16)
}

multi_registers = {
    "multi_input_L1_voltage": RegisterInfo(4500, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_input_L2_voltage": RegisterInfo(4501, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_input_L3_voltage": RegisterInfo(4502, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_input_L1_current": RegisterInfo(4503, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_input_L2_current": RegisterInfo(4504, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_input_L3_current": RegisterInfo(4505, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_input_L1_power": RegisterInfo(4506, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L2_power": RegisterInfo(4507, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L3_power": RegisterInfo(4508, INT16, UnitOfPower.WATT, 0.1),
    "multi_input_L1_frequency": RegisterInfo(4509, UINT16, FREQUENCY_HERTZ, 100),
    "multi_output_L1_voltage": RegisterInfo(4510, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_output_L2_voltage": RegisterInfo(4511, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_output_L3_voltage": RegisterInfo(4512, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_output_L1_current": RegisterInfo(4513, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_output_L2_current": RegisterInfo(4514, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_output_L3_current": RegisterInfo(4515, UINT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_output_L1_power": RegisterInfo(4516, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L2_power": RegisterInfo(4517, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L3_power": RegisterInfo(4518, INT16, UnitOfPower.WATT, 0.1),
    "multi_output_L1_frequency": RegisterInfo(4519, UINT16, FREQUENCY_HERTZ, 100),
    "multi_input_1_type": RegisterInfo(4520, UINT16),
    "multi_input_2_type": RegisterInfo(4521, UINT16),
    "multi_input_1_currentlimit": RegisterInfo(4522, UINT16, ELECTRIC_CURRENT_AMPERE, 10, SliderWriteType(0, 100)), #TODO make user configureable
    "multi_input_2_currentlimit": RegisterInfo(4523, UINT16, ELECTRIC_CURRENT_AMPERE, 10, SliderWriteType(0,100)), #TODO make user configureable
    "multi_numberofphases": RegisterInfo(4524, UINT16),
    "multi_activein_activeinput": RegisterInfo(4525, UINT16),
    "multi_battery_voltage": RegisterInfo(4526, UINT16, ELECTRIC_POTENTIAL_VOLT, 100),
    "multi_battery_current": RegisterInfo(4527, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "multi_battery_temperature": RegisterInfo(4528, INT16, UnitOfTemperature.CELSIUS, 10),
    "multi_battery_soc": RegisterInfo(4529, UINT16, PERCENTAGE, 10),
    "multi_state": RegisterInfo(4530, UINT16),
    "multi_mode": RegisterInfo(4531, UINT16), #TODO introduce mode enums
    "multi_alarm_hightemperature": RegisterInfo(4532, UINT16),
    "multi_alarm_highvoltage": RegisterInfo(4533, UINT16),
    "multi_alarm_highvoltageacout": RegisterInfo(4534, UINT16),
    "multi_alarm_lowtemperature": RegisterInfo(4535, UINT16),
    "multi_alarm_lowvoltage": RegisterInfo(4536, UINT16),
    "multi_alarm_lowvoltageacout": RegisterInfo(4537, UINT16),
    "multi_alarm_overload": RegisterInfo(4538, UINT16),
    "multi_alarm_ripple": RegisterInfo(4539, UINT16),
    "multi_yield_pv_power": RegisterInfo(4540, UINT16, UnitOfPower.WATT),
    "multi_yield_user": RegisterInfo(4541, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_relay": RegisterInfo(4542, UINT16),
    "multi_mppoperationmode": RegisterInfo(4543, UINT16),
    "multi_pv_voltage": RegisterInfo(4544, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_errorcode": RegisterInfo(4545, UINT16),
    "multi_energy_acin1toacout": RegisterInfo(4546, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_acin1toinverter": RegisterInfo(4548, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_acin2toacout": RegisterInfo(4550, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_acin2toinverter": RegisterInfo(4552, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_acouttoacin1": RegisterInfo(4554, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_acouttoacin2": RegisterInfo(4556, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_invertertoacin1": RegisterInfo(4558, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_invertertoacin2": RegisterInfo(4560, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_invertertoacout": RegisterInfo(4562, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_outtoinverter": RegisterInfo(4564, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_solartoacin1": RegisterInfo(4566, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_solartoacin2": RegisterInfo(4568, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_energy_solartoacout": RegisterInfo(4570, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "mutli_energy_solartobattery": RegisterInfo(4572, UINT32, UnitOfEnergy.KILO_WATT_HOUR, 100),
    "multi_history_yield_today": RegisterInfo(4574, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_maxpower_today": RegisterInfo(4575, UINT16, UnitOfPower.WATT),
    "multi_history_yield_yesterday": RegisterInfo(4576, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_maxpower_yesterday": RegisterInfo(4577, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_0_yield_today": RegisterInfo(4578, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_1_yield_today": RegisterInfo(4579, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_2_yield_today": RegisterInfo(4580, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_3_yield_today": RegisterInfo(4581, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_0_yield_yesterday": RegisterInfo(4582, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_1_yield_yesterday": RegisterInfo(4583, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_2_yield_yesterday": RegisterInfo(4584, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_3_yield_yesterday": RegisterInfo(4585, UINT16, UnitOfEnergy.KILO_WATT_HOUR, 10),
    "multi_history_tracker_0_maxpower_today": RegisterInfo(4586, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_1_maxpower_today": RegisterInfo(4587, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_2_maxpower_today": RegisterInfo(4588, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_3_maxpower_today": RegisterInfo(4589, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_0_maxpower_yesterday": RegisterInfo(4590, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_1_maxpower_yesterday": RegisterInfo(4591, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_2_maxpower_yesterday": RegisterInfo(4592, UINT16, UnitOfPower.WATT),
    "multi_history_tracker_3_maxpower_yesterday": RegisterInfo(4593, UINT16, UnitOfPower.WATT),
    "multi_tracker_0_voltage": RegisterInfo(4594, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_tracker_1_voltage": RegisterInfo(4595, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_tracker_2_voltage": RegisterInfo(4596, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_tracker_3_voltage": RegisterInfo(4597, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "multi_tracker_0_power": RegisterInfo(4598, UINT16, UnitOfPower.WATT),
    "multi_tracker_1_power": RegisterInfo(4599, UINT16, UnitOfPower.WATT),
    "multi_tracker_2_power": RegisterInfo(4600, UINT16, UnitOfPower.WATT),
    "multi_tracker_3_power": RegisterInfo(4601, UINT16, UnitOfPower.WATT),
    "multi_alarm_lowsoc": RegisterInfo(4602, UINT16)

}

system_registers = {
    "system_serial": RegisterInfo(800, STRING(6)),
    "system_relay_0": RegisterInfo(register=806, dataType=UINT16, writeType=SwitchWriteType()),
    "system_relay_1": RegisterInfo(register=807, dataType=UINT16, writeType=SwitchWriteType()),
    "system_pvonoutput_L1": RegisterInfo(808, UINT16, UnitOfPower.WATT),
    "system_pvonoutput_l1": RegisterInfo(809, UINT16, UnitOfPower.WATT),
    "system_pvonoutput_l1": RegisterInfo(810, UINT16, UnitOfPower.WATT),
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
    "system_input_source": RegisterInfo(826, INT16)
}

system_battery_registers = {
    "system_battery_voltage": RegisterInfo(840, UINT16, ELECTRIC_POTENTIAL_VOLT, 10),
    "system_battery_current": RegisterInfo(841, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "system_battery_power": RegisterInfo(842, INT16, UnitOfPower.WATT),
    "system_battery_soc": RegisterInfo(843, UINT16, PERCENTAGE),
    "system_battery_state": RegisterInfo(844, UINT16),
    "system_battery_amphours": RegisterInfo(845, UINT16, ELECTRIC_CURRENT_AMPERE, -10), # should be amp hours
    "system_battery_time_to_go": RegisterInfo(846, UINT16, TIME_SECONDS, 0)
}

system_dc_registers = {
    "system_dc_pv_power": RegisterInfo(850, UINT16, UnitOfPower.WATT),
    "system_dc_pv_current": RegisterInfo(851, INT16, ELECTRIC_CURRENT_AMPERE, 10)
}

system_charger_registers = {
    "system_charger_power": RegisterInfo(855, UINT16, UnitOfPower.WATT)
}

system_power_registers = {
    "system_system_power": RegisterInfo(860, INT16, UnitOfPower.WATT)
}

system_bus_registers = {
    "system_bus_charge_current": RegisterInfo(865, INT16, ELECTRIC_CURRENT_AMPERE, 10),
    "system_bus_charge_power": RegisterInfo(866, INT16, UnitOfPower.WATT)
}

valid_unit_ids = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
                   11, 12, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 
                   31, 32, 33, 34, 40, 41, 42, 43, 44, 45, 46, 100, 223, 
                   224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 
                   235, 236, 237, 238, 239, 242, 243, 245, 246, 247]

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
    "system_bus_registers": system_bus_registers
}    
