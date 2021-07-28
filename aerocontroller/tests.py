import pytest
import time
import math
# Replace libraries by fake ones
import sys
import fake_rpi

sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)

from aerocontroller.utils import parse_time, parse_temp, LEDReverseWrapper
from aerocontroller.controller import AeroController
from unittest.mock import call
from unittest import mock
import numpy as np
from freezegun import freeze_time



@pytest.mark.parametrize(
    "t,expected",
    [
        ("30h", 60*60*30),
        ("30m", 60*30),
        ("30s", 30),
        (30, 30),
    ]
)
def test_parse_time(t, expected):
    assert parse_time(t) == expected


@pytest.mark.parametrize(
    "t,unit,expected",
    [
        ("30F", 'F', 30),
        ("30C", 'F', 86),
        ("41F", 'C', 5),
        ("30C", 'C', 30),
    ]
)
def test_parse_temp(t, unit, expected):
    assert parse_temp(t, unit) == expected


class MockLED:
    def __init__(self, pin):
        self.pin = pin
    def on(self):
        pass
    def off(self):
        pass

class MockSensor:
    on = False
    def __init__(self, pin):
        self.pin = pin

    @property
    def value(self):
        return self.on


def gen_mock_twilio_client(calls):
    class MockTwilioClient:
        def __init__(self, sid, token):
            self.sid = sid
            self.token = token
            self.messages = self
            self.call_index = 0
        def create(self, to, from_, body):
            if self.call_index >= len(calls):
                raise ValueError("too many twilio calls")
            assert calls[self.call_index] in body
            self.call_index += 1
    return MockTwilioClient

def gen_mock_si7021(temp, humidity):
    class MockSI7021:
        def __init__(self):
            self.temp = temp
            self.humidity = humidity
        def get_temp(self, unit):
            return self.temp
        def get_humidity(self):
            return self.humidity
    return MockSI7021


@freeze_time('2021-07-18 12:30:00')
@mock.patch('aerocontroller.controller.LED', side_effect=MockLED)
@mock.patch('aerocontroller.controller.Button', side_effect=MockSensor)
def test_aerocontroller_normal(mock_led, mock_sensor):
    mock_si7021 = mock.patch("aerocontroller.controller.SI7021", gen_mock_si7021(70, 40))
    calls = ['turning on LED', 'turning on outpump']
    mock_twilio_client = mock.patch("aerocontroller.controller.TwilioClient", gen_mock_twilio_client(calls))
    MockSensor.on = True
    with mock_si7021, mock_twilio_client:
        controller = AeroController(env_path='aerocontroller/.env.test')
        controller.step()
        controller.step()

@freeze_time('2021-07-18 07:00:00')
@mock.patch('aerocontroller.controller.LED', side_effect=MockLED)
@mock.patch('aerocontroller.controller.Button', side_effect=MockSensor)
def test_aerocontroller_normal(mock_led, mock_sensor):
    mock_si7021 = mock.patch("aerocontroller.controller.SI7021", gen_mock_si7021(70, 40))
    calls = ['turning on LED', 'turning off outpump']
    mock_twilio_client = mock.patch("aerocontroller.controller.TwilioClient", gen_mock_twilio_client(calls))
    MockSensor.on = False
    with mock_si7021, mock_twilio_client:
        controller = AeroController(env_path='aerocontroller/.env.test')
        controller.step()
        controller.step()

@freeze_time('2021-07-18 04:00:00')
@mock.patch('aerocontroller.controller.LED', side_effect=MockLED)
@mock.patch('aerocontroller.controller.Button', side_effect=MockSensor)
def test_aerocontroller_normal(mock_led, mock_sensor):
    mock_si7021 = mock.patch("aerocontroller.controller.SI7021", gen_mock_si7021(70, 40))
    calls = ['turning off LED', 'turning off outpump']
    mock_twilio_client = mock.patch("aerocontroller.controller.TwilioClient", gen_mock_twilio_client(calls))
    MockSensor.on = False
    with mock_si7021, mock_twilio_client:
        controller = AeroController(env_path='aerocontroller/.env.test')
        controller.step()
        controller.step()

@mock.patch('aerocontroller.controller.LED', side_effect=MockLED)
@mock.patch('aerocontroller.controller.Button', side_effect=MockSensor)
def test_aerocontroller_extreme_measurements(mock_led, mock_sensor):
    mock_si7021 = mock.patch("aerocontroller.controller.SI7021", gen_mock_si7021(99.6, 100.1))
    calls = [
        'Temperature alert: 100 Degrees F',
        "Humidity alert: 100%",
        'turning on LED',
        'turning off outpump',
        'Temperature alert: 100 Degrees F',
        "Humidity alert: 100%",
    ]
    mock_twilio_client = mock.patch("aerocontroller.controller.TwilioClient", gen_mock_twilio_client(calls))
    MockSensor.on = False
    with mock_si7021, mock_twilio_client:
        controller = AeroController(env_path='aerocontroller/.env.test')
        freezer = freeze_time('2021-07-18 07:00:00')
        freezer.start()
        controller.step()
        controller.step()
        freezer.stop()
        freezer = freeze_time('2021-07-18 07:06:00')
        freezer.start()
        controller.step()
        controller.step()
        freezer.stop()
