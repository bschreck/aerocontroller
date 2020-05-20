# from relay import Relay
from w1thermsensor import W1ThermSensor
from .SI7021 import SI7021
from gpiozero import LED
# from signal import pause
import fire
import time
import sys


class W1SensorWrapper:
    def __init__(self, unit='F'):
        self.sensor = W1ThermSensor()
        self.unit = unit

    def get_temp(self):
        if self.unit == 'F':
            return self.sensor.get_temperature(W1ThermSensor.DEGREES_F)
        else:
            return self.sensor.get_temperature()


class Incubator:
    def __init__(self, temp=25, humidity=90, slack=1,
                 temp_sensor='SI7021', unit='C'):
        self.target_temp = temp
        self.target_humidity = humidity
        self.slack = slack
        if temp_sensor == 'SI7021':
            self.temp_sensor = SI7021()
        else:
            self.temp_sensor = W1SensorWrapper(unit=unit)
        self.light = LED('BOARD29')
        self.overhead_fan = LED('BOARD31')
        self.in_fan = LED('BOARD33')
        self.out_fan = LED('BOARD35')

    def set_cooling(self):
        print("Setting state to cooling")
        self.in_fan.on()
        self.out_fan.on()
        self.light.off()

    def set_heating(self):
        print("Setting state to heating")
        self.in_fan.off()
        self.out_fan.off()
        self.light.on()

    def set_drying(self):
        print("Setting state to drying")
        self.out_fan.on()
        self.overhead_fan.on()

    def set_humidifying(self):
        if not isinstance(self.temp_sensor, SI7021):
            return
        print("Setting state to humidifying")
        self.out_fan.off()
        self.overhead_fan.off()

    @property
    def too_hot(self):
        return self.temp > (self.target_temp + self.slack)

    @property
    def too_cold(self):
        return self.temp < (self.target_temp - self.slack)

    @property
    def too_dry(self):
        return self.humidity < (self.target_humidity - self.slack)

    @property
    def too_wet(self):
        return self.humidity > (self.target_humidity + self.slack)

    def adjust(self):
        self.temp = self.temp_sensor.get_tempC()
        if self.temp is None:
            self.temp = 1000
        if isinstance(self.temp_sensor, SI7021):
            self.humidity = self.temp_sensor.get_humidity()
            if self.humidity is None:
                self.humidity = 100

        print("Current State:")
        print(f"Target Temp = {self.target_temp}")
        print(f"Current Temp = {self.temp}")
        print(f"Target Humidity = {self.target_humidity}")
        print(f"Current Humidity = {self.humidity}")


        if self.too_hot:
            self.set_cooling()
        elif self.too_cold:
            self.set_heating()
            # fans cool things down too much
            self.set_humidifying()
        else:
            print("No temperature action taken")
        if self.too_hot and self.too_wet:
            self.set_cooling()
            self.set_drying()
        elif self.too_hot and self.too_dry:
            self.set_cooling()
            self.set_humidifying()
        sys.stdout.flush()


def adjust(temp=25, humidity=90, slack=1, interval=5,
           temp_sensor='SI7021', unit='C'):
    inc = Incubator(temp, humidity, slack, temp_sensor=temp_sensor,
                    unit=unit)
    while True:
        inc.adjust()
        time.sleep(interval)


def cli():
    fire.Fire(adjust)
