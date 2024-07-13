import struct
from dataclasses import dataclass
from typing import Optional

from pymodbus.client.base import ModbusBaseSyncClient

from smart_meter.polling_smart_meter import PollingSmartMeter
from smart_meter.smart_meter_packet import SmartMeterPacket, PhaseData, EnergyData


@dataclass
class ModbusAddresses:
    l1_voltage: Optional[int]
    l1_amperage: Optional[int]
    l1_power: Optional[int]
    l1_delivery: Optional[int]
    l1_redelivery: Optional[int]

    l2_voltage: Optional[int]
    l2_amperage: Optional[int]
    l2_power: Optional[int]
    l2_delivery: Optional[int]
    l2_redelivery: Optional[int]

    l3_voltage: Optional[int]
    l3_amperage: Optional[int]
    l3_power: Optional[int]
    l3_delivery: Optional[int]
    l3_redelivery: Optional[int]

    total_power: Optional[int]
    total_delivery: Optional[int]
    total_redelivery: Optional[int]

    frequency: Optional[int]

    gas: Optional[int]

    water: Optional[int]


class ModbusSmartMeter(PollingSmartMeter):

    def __init__(self, modbus_client: ModbusBaseSyncClient, modbus_addresses: ModbusAddresses, measurement_interval: float):
        super().__init__(measurement_interval)

        self.modbus_client = modbus_client
        self.modbus_addresses = modbus_addresses

        self.modbus_client.connect()

    def fetch_smart_meter_packet(self) -> SmartMeterPacket:
        addresses = self.modbus_addresses
        return SmartMeterPacket(
            phase_l1=self.fetch_phase_data(addresses.l1_voltage, addresses.l1_amperage, addresses.l1_power,
                                           addresses.l1_delivery, addresses.l1_redelivery),
            phase_l2=self.fetch_phase_data(addresses.l2_voltage, addresses.l2_amperage, addresses.l2_power,
                                           addresses.l2_delivery, addresses.l2_redelivery),
            phase_l3=self.fetch_phase_data(addresses.l3_voltage, addresses.l3_amperage, addresses.l3_power,
                                           addresses.l3_delivery, addresses.l3_redelivery),
            power=self.read_register(addresses.total_power),
            energy=self.fetch_energy_data(addresses.total_delivery, addresses.total_redelivery),
            frequency=self.read_register(addresses.frequency),
            gas=self.read_register(addresses.gas),
            water=self.read_register(addresses.water),
        )

    def fetch_phase_data(self, voltage_register: Optional[int], amperage_register: Optional[int],
                         power_register: Optional[int], delivery_register: Optional[int],
                         redelivery_register: Optional[int]) -> PhaseData:
        return PhaseData(
            voltage=self.read_register(voltage_register),
            amperage=self.read_register(amperage_register),
            power=self.read_register(power_register),
            energy=self.fetch_energy_data(delivery_register, redelivery_register),
        )

    def fetch_energy_data(self, delivery_register: Optional[int], redelivery_register: Optional[int]) -> Optional[EnergyData]:
        return EnergyData(
            delivery=self.read_register(delivery_register),
            redelivery=self.read_register(redelivery_register),
        )

    def read_register(self, address: Optional[int]) -> Optional[float]:
        if address is None:
            return None

        registers = self.modbus_client.read_holding_registers(address, 2, slave=1).registers
        combined_registers = (registers[0] << 16) | registers[1]
        float_value = struct.unpack('>f', struct.pack('>I', combined_registers))[0]

        return float_value
