# smart-meter-mqtt-bridge

A bridge for multiple "smart meters" (eg. electricity meters that can be read out digitally through serial or modbus) to a MQTT broker

## Environment variables

**MQTT variables**
- `MQTT_BROKER_ADDRESS` (defaults to `localhost`)
- `MQTT_BROKER_PORT` (defaults to `1883`)
- `MQTT_TOPIC_PREFIX` (defaults to `smart-meter`)
- `MQTT_QOS` (defaults to `0`)
- `MQTT_RETAIN` (defaults to `true`)

**Smart-meter variables**
- `SMART_METER_TYPE` (available types: `dts353f`, `sdm72dm`, `p1`)

Other smart-meter specific variables need to be present depending on which smart meter is connected. To figure out which environment variables are required by your smart meter, fill out only the `SMART_METER_TYPE` environment variable and look for errors when running the Docker image. Additional variables might have different defaults depending on the smart meter type, and include:
- `SMART_METER_CONNECTION_TYPE`
- `SMART_METER_SERIAL_PORT`
- `SMART_METER_SERIAL_BAUDRATE`
- `SMART_METER_SERIAL_BYTESIZE`
- `SMART_METER_SERIAL_PARITY`
- `SMART_METER_SERIAL_STOPBITS`
- `SMART_METER_SERIAL_TIMEOUT`
- `SMART_METER_TCP_ADDRESS`
- `SMART_METER_TCP_PORT`
- `SMART_METER_MEASUREMENT_INTERVAL`
- See `smart_meter/smart_meter_factory.py` for all smart-meter environment variables and information on how they are used.

## Supported smart meters

- `P1`, most Dutch smart electricity meters support this serial-based protocol
- `DTS353F`, a modbus electricity meter by YTL
- `SDM72D-M`, a modbus electricity meter by Eastron

## MQTT topics

Depending on which parameters are exposed by the electricity meter, it will publish to the following topics:
- `{prefix}/l1|l2|l3/voltage`: voltage in V
- `{prefix}/l1|l2|l3/amperage`: current in A
- `{prefix}/l1|l2|l3/power`: power in kW
- `{prefix}/l1|l2|l3/energy`: energy in kWh
- `{prefix}/l1|l2|l3/energy/delivery`: energy delivery in kWh
- `{prefix}/l1|l2|l3/energy/erdelivery`: energy redelivery in kWh
- `{prefix}/power`: total power in kW
- `{prefix}/energy`: total energy in kWh
- `{prefix}/energy/delivery`: total energy delivery in kWh
- `{prefix}/energy/redelivery`: total energy redelivery in kWh
- `{prefix}/frequency`: grid frequency in Hz
- `{prefix}/tariff`: current tariff, 1 (low) or 2 (high)
- `{prefix}/gas`: gas usage in m^3
- `{prefix}/water`: water usage in m^3

See `smart_meter/smart_meter_packet.py` for more information.
