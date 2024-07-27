from pymodbus.client.base import ModbusBaseSyncClient

from smart_meter.modbus_smart_meter import ModbusSmartMeter, ModbusAddresses, ModbusUnitConversion


# https://www.cfos-emobility.de/files/cfos-ytl-dts353-modbus-registers.pdf
class Sdm72dmSmartMeter(ModbusSmartMeter):
    def __init__(self, modbus_client: ModbusBaseSyncClient, measurement_interval: float):
        super().__init__(
            modbus_client=modbus_client,
            modbus_addresses=ModbusAddresses(
                total_power=0x0034,
                total_delivery=0x0048,
                total_redelivery=0x004A,

                frequency=None,

                l1_voltage=None,
                l1_amperage=None,
                l1_power=None,
                l1_delivery=None,
                l1_redelivery=None,

                l2_voltage=None,
                l2_amperage=None,
                l2_power=None,
                l2_delivery=None,
                l2_redelivery=None,

                l3_voltage=None,
                l3_amperage=None,
                l3_power=None,
                l3_delivery=None,
                l3_redelivery=None,

                gas=None,
                water=None,
            ),
            unit_conversion=ModbusUnitConversion(
                power=0.001,  # W -> kW
            ),
            modbus_register_type='input',
            measurement_interval=measurement_interval,
        )
