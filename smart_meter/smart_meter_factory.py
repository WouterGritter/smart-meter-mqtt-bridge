import os

from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from serial import Serial

from smart_meter.dts353f_smart_meter import Dts353fSmartMeter
from smart_meter.sdm72dm_smart_meter import Sdm72dmSmartMeter
from smart_meter.p1_smart_meter import P1SmartMeter

# Factory environment variable keys
SMART_METER_TYPE = 'SMART_METER_TYPE'
SMART_METER_CONNECTION_TYPE = 'SMART_METER_CONNECTION_TYPE'
SMART_METER_SERIAL_PORT = 'SMART_METER_SERIAL_PORT'
SMART_METER_SERIAL_BAUDRATE = 'SMART_METER_SERIAL_BAUDRATE'
SMART_METER_SERIAL_BYTESIZE = 'SMART_METER_SERIAL_BYTESIZE'
SMART_METER_SERIAL_PARITY = 'SMART_METER_SERIAL_PARITY'
SMART_METER_SERIAL_STOPBITS = 'SMART_METER_SERIAL_STOPBITS'
SMART_METER_SERIAL_TIMEOUT = 'SMART_METER_SERIAL_TIMEOUT'
SMART_METER_TCP_ADDRESS = 'SMART_METER_TCP_ADDRESS'
SMART_METER_TCP_PORT = 'SMART_METER_TCP_PORT'
SMART_METER_MEASUREMENT_INTERVAL = 'SMART_METER_MEASUREMENT_INTERVAL'


def build_smart_meter():
    sm_type = os.getenv(SMART_METER_TYPE)
    if sm_type == 'dts353f':
        return Dts353fSmartMeter(
            modbus_client=build_modbus_device(
                def_baudrate=9600,
                def_bytesize=8,
                def_parity='E',
                def_stopbits=1,
                def_timeout=0.5,
            ),
            measurement_interval=float(os.getenv(SMART_METER_MEASUREMENT_INTERVAL, '2.0'))
        )
    elif sm_type == 'sdm72dm':
        return Sdm72dmSmartMeter(
            modbus_client=build_modbus_device(
                def_baudrate=9600,
                def_bytesize=8,
                def_parity='N',
                def_stopbits=1,
                def_timeout=0.5,
            ),
            measurement_interval=float(os.getenv(SMART_METER_MEASUREMENT_INTERVAL, '2.0'))
        )
    elif sm_type == 'p1':
        return P1SmartMeter(
            serial_device=build_serial_device(
                def_baudrate=115200,
                def_bytesize=8,
                def_parity='N',
                def_stopbits=1,
                def_timeout=0.5,
            )
        )
    else:
        raise Exception(f'Invalid environment variable {SMART_METER_TYPE} "{sm_type}" (must be "dts353f" or "p1")')


def build_modbus_device(def_baudrate: int, def_bytesize: int, def_parity: str, def_stopbits: int, def_timeout: float):
    connection_type = os.getenv(SMART_METER_CONNECTION_TYPE)
    if connection_type == 'serial':
        port = os.getenv(SMART_METER_SERIAL_PORT)
        if port is None:
            raise Exception(f'Environment variable not defined but required: {SMART_METER_SERIAL_PORT}')
        return ModbusSerialClient(
            port=port,
            baudrate=int(os.getenv(SMART_METER_SERIAL_BAUDRATE, def_baudrate)),
            bytesize=int(os.getenv(SMART_METER_SERIAL_BYTESIZE, def_bytesize)),
            parity=os.getenv(SMART_METER_SERIAL_PARITY, def_parity),
            stopbits=int(os.getenv(SMART_METER_SERIAL_STOPBITS, def_stopbits)),
            timeout=float(os.getenv(SMART_METER_SERIAL_TIMEOUT, def_timeout)),
        )
    elif connection_type == 'tcp':
        host = os.getenv(SMART_METER_TCP_ADDRESS)
        port = int(os.getenv(SMART_METER_TCP_PORT, '502'))
        if host is None:
            raise Exception(f'Environment variable not defined but required: {SMART_METER_TCP_ADDRESS}')
        return ModbusTcpClient(
            host=host,
            port=port,
        )
    else:
        raise Exception(
            f'Invalid environment variable {SMART_METER_CONNECTION_TYPE} "{connection_type}" (must be "serial" or "tcp")')


def build_serial_device(def_baudrate: int, def_bytesize: int, def_parity: str, def_stopbits: int, def_timeout: float):
    port = os.getenv(SMART_METER_SERIAL_PORT)
    if port is None:
        raise Exception(f'Environment variable not defined but required: {SMART_METER_SERIAL_PORT}')
    return Serial(
        port=port,
        baudrate=int(os.getenv(SMART_METER_SERIAL_BAUDRATE, def_baudrate)),
        bytesize=int(os.getenv(SMART_METER_SERIAL_BYTESIZE, def_bytesize)),
        parity=os.getenv(SMART_METER_SERIAL_PARITY, def_parity),
        stopbits=int(os.getenv(SMART_METER_SERIAL_STOPBITS, def_stopbits)),
        timeout=float(os.getenv(SMART_METER_SERIAL_TIMEOUT, def_timeout)),
    )
