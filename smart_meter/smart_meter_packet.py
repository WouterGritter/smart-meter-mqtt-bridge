from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Self


class MqttDataClass(ABC):

    @abstractmethod
    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        pass


@dataclass
class EnergyData(MqttDataClass):
    delivery: Optional[float]  # kWh
    redelivery: Optional[float]  # kWh

    @property
    def total(self) -> Optional[float]:
        if self.delivery is None and self.redelivery is None:
            return None

        delivery = 0 if self.delivery is None else self.delivery
        redelivery = 0 if self.redelivery is None else self.redelivery
        return delivery - redelivery

    def to_topics(self, topic_prefix: str = '') -> dict[str, float]:
        topics = {}

        if self.total is not None:
            topics[f'{topic_prefix}'] = round(self.total, 3),

        if self.delivery is not None and self.redelivery is not None:
            topics[f'{topic_prefix}/delivery'] = round(self.delivery, 3)
            topics[f'{topic_prefix}/redelivery'] = round(self.redelivery, 3)

        return topics

    def reverse_energy_direction(self) -> Self:
        return EnergyData(
            delivery=self.redelivery,
            redelivery=self.delivery,
        )


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

    def reverse_power_direction(self) -> Self:
        if self.power is not None:
            return PhaseData(
                voltage=self.voltage,
                amperage=self.amperage,
                power=self.power * -1,
                energy=self.energy,
            )

        return self

    def reverse_energy_direction(self) -> Self:
        if self.energy is not None:
            return PhaseData(
                voltage=self.voltage,
                amperage=self.amperage,
                power=self.power,
                energy=self.energy.reverse_energy_direction(),
            )

        return self


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

    def reverse_power_direction(self) -> Self:
        return SmartMeterPacket(
            phase_l1=None if self.phase_l1 is None else self.phase_l1.reverse_power_direction(),
            phase_l2=None if self.phase_l2 is None else self.phase_l2.reverse_power_direction(),
            phase_l3=None if self.phase_l3 is None else self.phase_l3.reverse_power_direction(),
            power=None if self.power is None else self.power * -1,
            energy=self.energy,
            frequency=self.frequency,
            gas=self.gas,
            water=self.water,
        )

    def reverse_energy_direction(self) -> Self:
        return SmartMeterPacket(
            phase_l1=None if self.phase_l1 is None else self.phase_l1.reverse_energy_direction(),
            phase_l2=None if self.phase_l2 is None else self.phase_l2.reverse_energy_direction(),
            phase_l3=None if self.phase_l3 is None else self.phase_l3.reverse_energy_direction(),
            power=self.power,
            energy=None if self.energy is None else self.energy.reverse_energy_direction(),
            frequency=self.frequency,
            gas=self.gas,
            water=self.water,
        )
