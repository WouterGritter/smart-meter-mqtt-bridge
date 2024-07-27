from pymodbus.client.base import ModbusBaseSyncClient

from smart_meter.modbus_smart_meter import ModbusSmartMeter, ModbusAddresses


# https://www.cfos-emobility.de/files/cfos-ytl-dts353-modbus-registers.pdf
class Dts353fSmartMeter(ModbusSmartMeter):
    def __init__(self, modbus_client: ModbusBaseSyncClient, measurement_interval: float):
        super().__init__(
            modbus_client=modbus_client,
            modbus_addresses=ModbusAddresses(
                l1_voltage=0x000E,
                l1_amperage=0x0016,
                l1_power=0x001E,
                l1_delivery=0x010A,
                l1_redelivery=0x0112,

                l2_voltage=0x0010,
                l2_amperage=0x0018,
                l2_power=0x0020,
                l2_delivery=0x010C,
                l2_redelivery=0x0114,

                l3_voltage=0x0012,
                l3_amperage=0x001A,
                l3_power=0x0022,
                l3_delivery=0x010E,
                l3_redelivery=0x0116,

                total_power=0x001C,
                total_delivery=0x0108,
                total_redelivery=0x0110,

                frequency=0x0014,

                gas=None,
                water=None,
            ),
            modbus_register_type='holding',
            measurement_interval=measurement_interval,
        )
