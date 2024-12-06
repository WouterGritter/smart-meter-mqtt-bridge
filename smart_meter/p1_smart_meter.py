from typing import Callable, Optional

import serial

from smart_meter.smart_meter import SmartMeter
from smart_meter.smart_meter_packet import SmartMeterPacket, PhaseData, EnergyData


# https://github.com/jvhaarst/DSMR-P1-telegram-reader/blob/master/documentation/Dutch%20Smart%20Meter%20Requirements%20v5.0.2%20Final%20P1.pdf
class P1SmartMeter(SmartMeter):
    def __init__(self, serial_device: serial.Serial):
        self.serial_device = serial_device

    def start_measuring(self, packet_callback: Callable[[SmartMeterPacket], None]):
        while True:
            measurement = self.fetch_measurement()
            packet_callback(measurement)

    def fetch_measurement(self) -> SmartMeterPacket:
        packet = self.read_p1_packet()

        l1_voltage = find_measurement(packet, '32.7.0')
        l1_power = find_measurement(packet, '21.7.0') - find_measurement(packet, '22.7.0')
        l1_amperage = (l1_power * 1000.0) / l1_voltage

        l2_voltage = find_measurement(packet, '52.7.0')
        l2_power = find_measurement(packet, '41.7.0') - find_measurement(packet, '42.7.0')
        l2_amperage = (l2_power * 1000.0) / l2_voltage

        l3_voltage = find_measurement(packet, '72.7.0')
        l3_power = find_measurement(packet, '61.7.0') - find_measurement(packet, '62.7.0')
        l3_amperage = (l3_power * 1000.0) / l3_voltage

        return SmartMeterPacket(
            phase_l1=PhaseData(
                voltage=l1_voltage,
                amperage=l1_amperage,
                power=l1_power,
            ),
            phase_l2=PhaseData(
                voltage=l2_voltage,
                amperage=l2_amperage,
                power=l2_power,
            ),
            phase_l3=PhaseData(
                voltage=l3_voltage,
                amperage=l3_amperage,
                power=l3_power,
            ),
            power=find_measurement(packet, '1.7.0') - find_measurement(packet, '2.7.0'),
            energy=EnergyData(
                delivery=find_measurement(packet, '1.8.1') + find_measurement(packet, '1.8.2'),
                redelivery=find_measurement(packet, '2.8.1') + find_measurement(packet, '2.8.2')
            ),
            tariff='high' if find_measurement(packet, '96.14.0') == 2 else 'low',

            # I think this will break when you are only/also measuring water usage, as it uses the same OBIS reference.
            # This might require looking at the equipment identifier.
            gas=find_measurement(packet, '24.2.1', 1),
            water=None,
        )

    def read_p1_packet(self) -> list[str]:
        try:
            packet = []
            line = ''

            while '!' not in line:
                line = self.serial_device.readline().decode()
                line = line.replace('\r', '')
                packet.append(line)

            return packet
        except:
            return []


def find_measurement(p1_packet: list[str], obis_reference: str, value_index: int = 0) -> Optional[float]:
    lines = list(filter(lambda line: obis_reference in line, p1_packet))
    if len(lines) == 0:
        return None

    values = lines[0].split('(')[1:]
    values = [d[0:-1] for d in values]

    if len(values) <= value_index:
        return None

    value = values[value_index]
    return float(value.split('*', 2)[0])
