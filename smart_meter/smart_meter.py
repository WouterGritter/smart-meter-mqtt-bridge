from abc import ABC, abstractmethod
from typing import Callable

from smart_meter.smart_meter_packet import SmartMeterPacket


class SmartMeter(ABC):

    @abstractmethod
    def start_measuring(self, packet_callback: Callable[[SmartMeterPacket], None]):
        pass
