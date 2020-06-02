import pytest
from kojifier.utils import parse_time, parse_temp, W1SensorWrapper, LEDReverseWrapper
from kojifier.auto_fermenter import AutoFermenter
from unittest.mock import call
from unittest import mock


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
    def __init__(self):
        self.calls = 0
    def get_temp(self, degrees):
        if self.calls > 1:
            return 88
        self.calls += 1
        return 25

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


@mock.patch('kojifier.auto_fermenter.W1SensorWrapper', side_effect=MockW1ThermSensor)
@mock.patch('kojifier.auto_fermenter.LED', side_effect=MockLED)
def test_auto_fermenter_tempeh(mock_led, mock_sensor):
    fermenter = AutoFermenter(config='kojifier/test_tempeh_config.yaml', env_path='kojifier/.env.test')
    with mock.patch.object(fermenter, 'twilio_client', MockTwilioClient('sid', 'token')):
        fermenter.make_tempeh()
