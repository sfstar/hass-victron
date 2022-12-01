[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Victron GX modbusTCP integration
This integration scans for all available registers of a provided GX device.
It then uses the defined register ledgers to create entities for each and every register that is provided by the GX device.

# Project release state
Please note that the integration is currently in an beta state.
This means that although the integration should work it might encounter unforeseen bugs and breaking changes to configuration options.
Testers are welcome to try out the integration and submit issues / feature requests.

## Limitations
The current state of this integration provides the following limitations regarding it's use:
- Applying config changes requires a reload/restart of the integration
- Number slider options aren't yet fully based on user specified limits
- Configuring the integration will be relatively slow if a discovery scan is required.


## Currently planned improvements
TODO
- Fully Switch to async
- Investigate if scan without causing errors is possible
- Determine limit applicability by specifying AC or DC in register info writetype
- Expose this integration to hacs
- Start using releases and release notes
- Improve connection loss resilience

# Installing the integration
You can install this integration by following the steps for your preferred installation method

## Warning
This integration uses pymodbus 3.0.2 or higher.
As of november 2022 the built-in home assistant modbus integration runs on a version < 3.0.0
If you install this integration the built-in modbus integration will stop to work due to breaking changes between 2.x.x and 3.0.0

## Manual
1. Clone the repository to your machine.
2. Copy the contents of custom_components/ to your machine running home assistant.
3. Restart home assistant
4. goto "settings -> devices and services -> integration"
5. click on "add integration"
6. Search for "victron"
7. Fill in the correct options and submit

## HACS

### Custom repository
1. Add https://github.com/sfstar/hass-victron to your HACS custom repositories.
2. Install through HACS. 
3. Restart Home Assistant. 
4. Add the integration through your settings.

### Default
Currently not explicitly supported (although you could add the repo as an custom repository in hacs)
TODO 

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

## interval
interval determines the number of rounded seconds to use between updating the entities provided by this integration.
For slower systems setting the interval to lower than 5 seconds might cause issues.
Setting a interval of 0 will result in an interval of 1 seconds being used.

# Resources 
The following links can be helpfull resources:
- [setting up modbusTCP on the gx device](https://www.victronenergy.com/live/ccgx:modbustcp_faq)
