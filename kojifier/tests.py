import pytest
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

        # range is [-10, 10]
        temp_slope = (self.fermenter.new_hot_plate_power - 50) / 5
        if temp_slope < 0:
            if self.temp > 25:
                # linear to room temp
                self.temp -= .1
            return self.temp
        else:
            import pdb; pdb.set_trace()
            # make temperature a logistic fn
            max_temp = 500
            # gain is pid power
            dt = temp_slope * (1 - (self.temp / max_temp)) * self.temp
            if np.isinf(dt) or np.isnan(dt):
                # TODO: figure this out
                import pdb; pdb.set_trace()
            self.temp += dt
            print(self.temp)
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
