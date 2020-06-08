import pytest
import time
import math
# Replace libraries by fake ones
import sys
import fake_rpi

sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)

from kojifier.utils import parse_time, parse_temp, LEDReverseWrapper
from kojifier.auto_fermenter import AutoFermenter
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

class MockW1ThermSensor:
    def __init__(self, fermenter):
        self.calls = 0
        self.fermenter = fermenter
        self.dts = []
        self.temps = []
        self.powers = []
        self.time_since_cooling = 0
        self.previous_time = None
    def get_temp(self, degrees):
        if self.calls < 20:
            self.calls += 1
            self.temp = 130
            return self.temp
        elif self.calls == 20:
            self.calls += 1
            self.temp = 88
            return self.temp
        self.calls += 1
        self.fermenter.pid.reset()

        min_temp = 75
        max_temp = 500
        p = self.fermenter.new_hot_plate_power
        current_time = time.time()
        dt = current_time - (self.previous_time or current_time)
        self.previous_time = current_time
        if p == 0:
            if self.temp > min_temp:
                self.temp -= .02 * dt
        else:
            if self.temp < max_temp:
                self.temp += p * dt
        self.powers.append(p)
        self.temps.append(self.temp)
        return self.temp


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
            assert 'Starting to incubate' in body
        elif self.calls == 1:
            assert 'done' in body
        else:
            raise ValueError("too many calls")
        self.calls += 1


@mock.patch('kojifier.utils.LED', side_effect=MockLED)
@mock.patch('kojifier.auto_fermenter.W1SensorWrapper', side_effect=MockW1ThermSensor)
def test_auto_fermenter_tempeh(mock_led, mock_sensor):
    fermenter = AutoFermenter(config='kojifier/test_tempeh_config.yaml', env_path='kojifier/.env.test')
    with mock.patch.object(fermenter, 'twilio_client', MockTwilioClient('sid', 'token')):
        fermenter.make_tempeh()
