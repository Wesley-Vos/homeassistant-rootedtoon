# Home-Assistant Rooted Toon custom integration (WIP)

This repostiory contains an Home-Assistant integration for a RootedToon. The integration is heavily based on the original Toon (cloud) integration and has support for:
- Controlling the climate/ thermomstat device
  - Climate Entity for the thermostat
  - Binary sensors for
    - Boiler is burning
    - Boiler is burning for heating
    - Boiler is burning for preheating
    - Boiler is burning for tapwater
    - Boiler error status
    - If the program is overriden
  - Sensors for:
    - Boiler modulation level percentage
    - Boiler Pressure (if boiler endpoint is enabled in the config and your boiler exposes the pressure through the OpenthermGateway
    - Actual temperature measured by the thermostat
    - Setpoint temperature of the thermostat
    - Sensor holding name of the next program (if program is on)
  - Calender entity:
    - Containing events for the built-in program for the upcoming week
    
- Reading a connected P1 Meter (if connected):
  - Sensors per tariff for:
    - Actual power usage
    - Actual power delivery
    - Total power used counter
    - Total power delivered counter
  - Sensors for:
    - Summed versions (by tariff) of the sensors above
  - Gas meter (if available):
    - Gas used last hour
    - Total gas used counter
  - Any connected smart plugs:
     - Actual power usage
     - Total power used counter
     
## Deployment
To add the integration:
1. Add this repository to your HACS list of repositories
2. Download the RootedToon integration
3. Restart Home-Assistant
4. Add the integration through the integration overview
5. Enter some details:
  1. Name of the integration, in case you want multiple
  2. The IP adress of the Toon
  3. The port, by default 80
  4. If you want to enable the boiler endpoint, to read the boiler pressure only (disable if your boiler does not expose this)
  5. The scan interval for the boiler, don't set it higher than necessary. The pressure is not changing that often (keep at default if you have disabled the endpoint)
  6. Any additional prefix/ suffix texts for the boiler related entities
  7. If you want to enable the P1 meter endpoint, to read meter readings (disable if you don't have a P1 Meter)
  8. The scan interval for the P1 meter (keep at default if you have disabled the endpoint)
  9. Any additional prefix/ suffix texts for P1 Meter related entities
  10. If you want to enable the program endpoint, to get the built-in program
  11. The scan interval of the program (if enabled in step 5.10), keep this low, because your program does not change that often.
  12. The scan interval of the Thermostat endpoint (always enabled), set this somewhat lower if you want more accurate boiler modulation levels
  13. Any additional prefix/ suffix texts for thermostat related entities.
  
  
Overall note, think well about the scan intervals, don't put them lower (i.e. too many updates) than needed because your Toon does not like that much requests (especially the Toon 1).
