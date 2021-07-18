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


class MockTwilioClient:
    def __init__(self, sid, token):
        self.sid = sid
        self.token = token
        self.messages = self
        self.calls = 0
    def create(self, to, from_, body):
        if self.calls == 0:
            assert 'turning on LED' in body
        elif self.calls == 1:
            assert 'turning on outpump' in body
        else:
            raise ValueError("too many calls")
        self.calls += 1

class MockSI7021:
    def get_temp(self, unit):
        return 70
    def get_humidity(self):
        return 40


@mock.patch('aerocontroller.controller.LED', side_effect=MockLED)
def test_auto_fermenter_tempeh(mock_led):
    mock_si7021 = mock.patch("aerocontroller.controller.SI7021", MockSI7021)
    mock_twilio_client = mock.patch("aerocontroller.controller.TwilioClient", MockTwilioClient)
    with mock_si7021, mock_twilio_client:
        controller = AeroController(env_path='aerocontroller/.env.test')
        controller.run()
