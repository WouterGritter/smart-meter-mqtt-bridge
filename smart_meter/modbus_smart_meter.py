import struct
from dataclasses import dataclass
from typing import Optional, Literal

from pymodbus.client.base import ModbusBaseSyncClient

from smart_meter.polling_smart_meter import PollingSmartMeter
from smart_meter.smart_meter_packet import SmartMeterPacket, PhaseData, EnergyData


@dataclass
class ModbusAddresses:
    l1_voltage: Optional[int] = None
    l1_amperage: Optional[int] = None
    l1_power: Optional[int] = None
    l1_delivery: Optional[int] = None
    l1_redelivery: Optional[int] = None

    l2_voltage: Optional[int] = None
    l2_amperage: Optional[int] = None
    l2_power: Optional[int] = None
    l2_delivery: Optional[int] = None
    l2_redelivery: Optional[int] = None

    l3_voltage: Optional[int] = None
    l3_amperage: Optional[int] = None
    l3_power: Optional[int] = None
    l3_delivery: Optional[int] = None
    l3_redelivery: Optional[int] = None

    total_power: Optional[int] = None
    total_delivery: Optional[int] = None
    total_redelivery: Optional[int] = None

    frequency: Optional[int] = None

    gas: Optional[int] = None

    water: Optional[int] = None


@dataclass
class ModbusUnitConversion:
    # Modbus values are multiplied by the factors defined below, and should result in the commented unit.
    voltage: Optional[float] = None  # -> V
    amperage: Optional[float] = None  # -> A
    power: Optional[float] = None  # -> kW
    energy: Optional[float] = None  # -> kWh
    frequency: Optional[float] = None  # -> Hz
    gas: Optional[float] = None  # -> m^3
    water: Optional[float] = None  # -> m^3


class ModbusSmartMeter(PollingSmartMeter):

    def __init__(self, modbus_client: ModbusBaseSyncClient, modbus_addresses: ModbusAddresses, unit_conversion: ModbusUnitConversion, modbus_register_type: Literal['holding', 'input'], measurement_interval: float):
        super().__init__(measurement_interval)

        self.modbus_client = modbus_client
        self.modbus_addresses = modbus_addresses
        self.unit_conversion = unit_conversion
        self.modbus_register_type = modbus_register_type

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
            power=self.read_register(addresses.total_power, self.unit_conversion.power),
            energy=self.fetch_energy_data(addresses.total_delivery, addresses.total_redelivery),
            frequency=self.read_register(addresses.frequency, self.unit_conversion.frequency),
            gas=self.read_register(addresses.gas, self.unit_conversion.gas),
            water=self.read_register(addresses.water, self.unit_conversion.water),
        )

    def fetch_phase_data(self, voltage_register: Optional[int], amperage_register: Optional[int],
                         power_register: Optional[int], delivery_register: Optional[int],
                         redelivery_register: Optional[int]) -> PhaseData:
        return PhaseData(
            voltage=self.read_register(voltage_register, self.unit_conversion.voltage),
            amperage=self.read_register(amperage_register, self.unit_conversion.amperage),
            power=self.read_register(power_register, self.unit_conversion.power),
            energy=self.fetch_energy_data(delivery_register, redelivery_register),
        )

    def fetch_energy_data(self, delivery_register: Optional[int], redelivery_register: Optional[int]) -> Optional[EnergyData]:
        return EnergyData(
            delivery=self.read_register(delivery_register, self.unit_conversion.energy),
            redelivery=self.read_register(redelivery_register, self.unit_conversion.energy),
        )

    def read_register(self, address: Optional[int], unit_correction_factor: Optional[float]) -> Optional[float]:
        if address is None:
            return None

        if self.modbus_register_type == 'holding':
            registers = self.modbus_client.read_holding_registers(address, 2, slave=1).registers
        elif self.modbus_register_type == 'input':
            registers = self.modbus_client.read_input_registers(address, 2, slave=1).registers
        else:
            raise Exception(f'Invalid modbus_register_type \'{self.modbus_register_type}\'')

        combined_registers = (registers[0] << 16) | registers[1]
        float_value = struct.unpack('>f', struct.pack('>I', combined_registers))[0]

        if unit_correction_factor is not None:
            float_value = float_value * unit_correction_factor

        return float_value
