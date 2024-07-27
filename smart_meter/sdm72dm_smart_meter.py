from pymodbus.client.base import ModbusBaseSyncClient

from smart_meter.modbus_smart_meter import ModbusSmartMeter, ModbusAddresses, ModbusUnitConversion


# https://docs.vekto.nl/media/eastron/eastron-sdm72dm-user-manual-v1.5.pdf
class Sdm72dmSmartMeter(ModbusSmartMeter):
    def __init__(self, modbus_client: ModbusBaseSyncClient, measurement_interval: float):
        super().__init__(
            modbus_client=modbus_client,
            modbus_addresses=ModbusAddresses(
                total_power=0x0034,
                total_delivery=0x0048,
                total_redelivery=0x004A,
            ),
            unit_conversion=ModbusUnitConversion(
                power=0.001,  # W -> kW
            ),
            modbus_register_type='input',
            measurement_interval=measurement_interval,
        )
