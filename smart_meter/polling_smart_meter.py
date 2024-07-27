import time
from abc import abstractmethod, ABC
from typing import Callable

from smart_meter.smart_meter import SmartMeter
from smart_meter.smart_meter_packet import SmartMeterPacket


class PollingSmartMeter(SmartMeter, ABC):
    def __init__(self, measurement_interval: float):
        self.measurement_interval = measurement_interval

    def start_measuring(self, packet_callback: Callable[[SmartMeterPacket], None]):
        time.sleep(self.measurement_interval)

        while True:
            start = time.time()
            try:
                packet = self.fetch_smart_meter_packet()
            except Exception as ex:
                print(f'An error occurred while fetching smart meter packet: {ex}')
                continue

            try:
                packet_callback(packet)
            except Exception as ex:
                print(f'An error occurred while processing smart meter packet: {ex}')

            elapsed = time.time() - start
            time.sleep(max(0.0, self.measurement_interval - elapsed))


    @abstractmethod
    def fetch_smart_meter_packet(self) -> SmartMeterPacket:
        pass
