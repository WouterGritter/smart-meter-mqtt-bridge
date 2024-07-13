import os

import paho.mqtt.client as mqtt

from typing import Optional

from dotenv import load_dotenv

from smart_meter.smart_meter_factory import build_smart_meter
from smart_meter.smart_meter_packet import SmartMeterPacket

load_dotenv()


MQTT_BROKER_ADDRESS = os.getenv('MQTT_BROKER_ADDRESS', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', 'smart-meter')
MQTT_QOS = int(os.getenv('MQTT_QOS', '0'))
MQTT_RETAIN = os.getenv('MQTT_RETAIN', 'true') == 'true'


mqttc: Optional[mqtt.Client] = None


def packet_callback(packet: SmartMeterPacket):
    topics = packet.to_topics(topic_prefix=MQTT_TOPIC_PREFIX)
    for topic, value in topics.items():
        mqttc.publish(topic=topic, payload=value, qos=MQTT_QOS, retain=MQTT_RETAIN)


def main():
    global mqttc

    print(f'smart-meter-mqtt-bridge version {os.getenv("IMAGE_VERSION")}')

    print(f'{MQTT_BROKER_ADDRESS=}')
    print(f'{MQTT_BROKER_PORT=}')
    print(f'{MQTT_TOPIC_PREFIX=}')
    print(f'{MQTT_QOS=}')
    print(f'{MQTT_RETAIN=}')

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, 60)
    mqttc.loop_start()

    smart_meter = build_smart_meter()
    print(f'Loaded smart meter {smart_meter.__class__.__name__}. Starting measurements.')

    smart_meter.start_measuring(packet_callback)


if __name__ == '__main__':
    main()
