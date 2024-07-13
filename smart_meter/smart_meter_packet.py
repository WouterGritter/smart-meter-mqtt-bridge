from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class MqttDataClass(ABC):

    @abstractmethod
    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        pass


@dataclass
class EnergyData(MqttDataClass):
    delivery: float  # kWh
    redelivery: Optional[float]  # kWh

    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        if self.redelivery is None:
            return {
                f'{topic_prefix}': self.delivery,
            }
        else:
            return {
                f'{topic_prefix}': round(self.delivery - self.redelivery, 3),
                f'{topic_prefix}/delivery': round(self.delivery, 3),
                f'{topic_prefix}/redelivery': round(self.redelivery, 3),
            }


@dataclass
class PhaseData(MqttDataClass):
    voltage: Optional[float]  # V
    amperage: Optional[float]  # A
    power: Optional[float]  # kW
    energy: Optional[EnergyData]

    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        topics = {}
        if self.voltage is not None:
            topics[f'{topic_prefix}/voltage'] = round(self.voltage, 1)
        if self.amperage is not None:
            topics[f'{topic_prefix}/amperage'] = round(self.amperage, 2)
        if self.power is not None:
            topics[f'{topic_prefix}/power'] = round(self.power, 3)
        if self.energy is not None:
            topics.update(self.energy.to_topics(f'{topic_prefix}/energy'))

        return topics


@dataclass
class SmartMeterPacket(MqttDataClass):
    phase_l1: Optional[PhaseData]
    phase_l2: Optional[PhaseData]
    phase_l3: Optional[PhaseData]
    power: Optional[float]  # kW
    energy: Optional[EnergyData]
    frequency: Optional[float]  # Hz
    gas: Optional[float]  # m^3
    water: Optional[float]  # m^3

    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        topics = {}
        if self.phase_l1 is not None:
            topics.update(self.phase_l1.to_topics(f'{topic_prefix}/l1'))
        if self.phase_l2 is not None:
            topics.update(self.phase_l2.to_topics(f'{topic_prefix}/l2'))
        if self.phase_l3 is not None:
            topics.update(self.phase_l3.to_topics(f'{topic_prefix}/l3'))
        if self.power is not None:
            topics[f'{topic_prefix}/power'] = round(self.power, 3)
        if self.energy is not None:
            topics.update(self.energy.to_topics(f'{topic_prefix}/energy'))
        if self.frequency is not None:
            topics[f'{topic_prefix}/frequency'] = round(self.frequency, 3)
        if self.gas is not None:
            topics[f'{topic_prefix}/gas'] = round(self.gas, 3)
        if self.water is not None:
            topics[f'{topic_prefix}/water'] = round(self.water, 3)

        return topics
