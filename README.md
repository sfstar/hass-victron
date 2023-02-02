[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Victron GX modbusTCP integration
This integration scans for all available registers of a provided GX device.
It then uses the defined register ledgers to create entities for each and every register that is provided by the GX device.

# Project release state
Please note that the integration is currently in an acceptance state.
This means that there are no breaking changes planned.
If a breaking change were to be introduced expect the release notes to reflect this.
If you are missing a feature or experience any issues please report them in the issue tracker.

## Limitations
The current state of this integration provides the following limitations regarding it's use:
- Configuring the integration will be relatively slow if a discovery scan is required.
- This integration wasn't tested with a three phase system. Although basic functionality should work minor bugs could have gone unnoticed

## Important Note
This integration was written an tested with the latest victron firmware running.
GX version: v2.92
Multiplus version: 492

Victron continuously improves upon the modbus implementation by adding new registers.
Therefore older firmware versions might not expose all registers this integration expects to be present.
This might (depending on your firmware and connected devices) cause odd behaviour where some but not all devices connected to your GX device will be correctly detected by this integration.

The best solution for this issue is to upgrade to the latest firmware.
You can also open an issue to get your firmware version supported.
This issue should contain the following information:
- Connected devices
- Firmware versions of the connected devices
- Missing device type (grid, vebus, bms can etc)
- Missing unit id (among other 30, 100, 227, 228)

Please note that it might take some time for older firmware versions to get full support (after a ticket is opened).


## Important Note 2
Victron is currently working on a new major release of the GX device (v3.x.x).
Currently this is still a pre release and since the documentation regarding the modbus register changes hasn't been made available this integration will only support v2.x GX device versions.

When the spec for V3 is released support for it will be added to the integration as well

## Currently planned improvements
- Fully Switch to async
- Investigate if scan without causing (ignorable) errors at the gx device is possible
- Improve connection loss resilience (mark / unmark availability of entities)
- Revisit datatypes used for storing register info

# Installing the integration
You can install this integration by following the steps for your preferred installation method

## Warning
This integration uses pymodbus 3.0.2 or higher.
As of november 2022 the built-in home assistant modbus integration runs on a version < 3.0.0
If you install this integration the built-in modbus integration will stop to work due to breaking changes between 2.x.x and 3.0.0

## Important announcement:
Starting from homeassistant core version 2023.2.x the built-in modbus integration now uses pymodbus version 3.1.1.
Version 0.0.7 (and up) of this integration will also use the 3.1.1 pymodbus version.

Although core version >= 2023.2 and previous versions of this integration should be compatible it is recommended that all users update both core and this integration in the same patch round.
Since having multiple library version requirements might cause the built-in 3.1.1 library to be overwritten by 3.0.2 reference of versions 0.0.6 and earlier.
This could cause issues if you are using specific configuration options of the built-in modbus integration that weren't working with pymodbus 3.0.2 and were fixed in 3.1.1

## Manual
1. Clone the repository to your machine.
2. Copy the contents of custom_components/ to your machine running home assistant.
3. Restart home assistant
4. goto "settings -> devices and services -> integration"
5. click on "add integration"
6. Search for "victron"
7. Fill in the correct options and submit

## HACS

### Default
1. Add the integration through this link: 
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sfstar&repository=hass-victron&category=integration)
3. Restart home assistant
4. Setup integration via the integration page.

# GX device errors
The integration scans for available units and register ranges upon installation and when selected in the options menu.
This will cause "errors" in the GX device under "settings -> services -> modbus TCP" due to not every register set and unit being available (and victron not providing a discover unit / register to query)
These errors can be cleared without any issue and should not be reported unless (after scanning) errors keep getting reported.

# Disclaimer
This integration speaks to the victron GX device.
The GX device is an exposed integration point for a system capable of running on high voltages and currents.
If the system were to become unstable it might lead to damage of equipment, fires and/or electrocution.
Although this integration speaks to the (exposed by victron) modbusTCP server it might cause the system to become unstable in circumstances like (but not limited to):
- High request frequency
- (when implemented) writing to write_registers (for example changing the ess setpoint value)

Therefore the following applies to anyone using this code:
- This code is provided as is. 
- The developer does not assume any liability for issues caused by the use of this integration.
- Use at your own risk.

# Options
The integration provides end users with the following configuration options.

## Host
The IP address of the victron GX device running the modbusTCP service.
It's only configureable during setup and it's recommended to make the GX device static in your router

## Port
The port on which victron exposes the modbusTCP service.
Victron exposes the service on port 502, but this configuration option is present to allow for proxy configuration (via nginx etc).
The average user doesn't need to change the port being used

## Interval
interval determines the number of rounded seconds to use between updating the entities provided by this integration.
For slower systems setting the interval to lower than 5 seconds might cause issues.
Setting a interval of 0 will result in an interval of 1 seconds being used.

## Advanced
Ticking the write support option enables an "advanced" users mode.
If write support is disabled the integration is "safer" to use.
Since you can't accidentally change any setting that might cause damage (i.e. to High currents for your cabling).

It is currently unknown and untested if the ModbusTCP server write registers are guard-railed. (Have protections/limits in place that prevent damage)
Therefore, this integration offers users the ability to set "soft" guard rails by requiring current and voltage settings and limits to be specified by the end user.
Although this make the integration safer, one should always double check if the provided write entities aren't capable of going to high / low for your system.

Currently the options are tailored to the US / EU base settings and lifepo4 battery voltages.
If you use another grid specification or battery type you can submit an issue to have them included.

### AC Current
The maximum current in Amps that your system is designed to handle.
This doesn't make a difference between the AC OUT and the AC IN side of your setup.
Please keep a small margin below your rated grid connection current (for example if you have 1x40A then set the integration to max 39 AMPS).

This advice does assume that your system is fully setup to handle these currents.

### DC current
The maximum current in Amps that your battery and battery cabling/busbars are rated to handle.

### DC Voltage
The voltage profile to use in order to calculate the voltage boundaries (i.e. 4s, 8s and 16s lifepo4 configurations).

### AC Voltage
The AC voltage for a single phase in your region (currently supported is US: 120v and EU: 230v)
This setting is used in combination with AC current to automatically calcultate the max wattage for applicable wattage settings.

# Resources 
The following links can be helpfull resources:
- [setting up modbusTCP on the gx device](https://www.victronenergy.com/live/ccgx:modbustcp_faq)
