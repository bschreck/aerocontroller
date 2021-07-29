import datetime as dt
import sys
# switch is 8/gpio14

from .SI7021 import SI7021
from gpiozero import LED, Button
import time
from twilio.rest import Client as TwilioClient
import math
from dotenv import load_dotenv
import os
import fire

class AeroController:
    def __init__(self, env_path, text=False, debug=False):
        self.env_path = env_path
        load_dotenv(dotenv_path=self.env_path)
        self.text = text
        self.debug = debug
        if self.text:
            self.twilio_sid = os.environ.get("TWILIO_SID")
            self.twilio_token = os.environ.get("TWILIO_TOKEN")
            self.twilio_from_number = os.environ.get("TWILIO_FROM_NUMBER")
            self.twilio_to_number = os.environ.get("TWILIO_TO_NUMBER")
            self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_token)

        self.low_humidity_threshold = int(os.environ.get("LOW_HUMIDITY_THRESHOLD"))
        self.high_humidity_threshold = int(os.environ.get("HIGH_HUMIDITY_THRESHOLD"))
        self.low_temp_threshold = int(os.environ.get("LOW_TEMP_THRESHOLD"))
        self.high_temp_threshold = int(os.environ.get("HIGH_TEMP_THRESHOLD"))
        self.led_start_hour = int(os.environ.get("LED_START_HOUR"))
        self.led_end_hour = int(os.environ.get("LED_END_HOUR"))
        self.outpump_start_hour = int(os.environ.get("OUTPUMP_START_HOUR"))
        self.outpump_end_hour = int(os.environ.get("OUTPUMP_END_HOUR"))
        self.inpump_on_seconds = int(os.environ.get("INPUMP_ON_SECONDS"))
        self.alert_wait_time_seconds = int(os.environ.get("ALERT_WAIT_TIME_SECONDS"))

        self.si7021 = SI7021()
        self.light = LED('BOARD11')
        self.water_level_sensor = Button('BOARD12')
        self.inpump = LED('BOARD18')
        self.outpump = LED('BOARD16')
        self.led_state = False
        self.inpump_state = False
        self.outpump_state = False
        self.previous_alert_times = {}
        self.reset_day()

    def turn_light_on(self):
        if self.debug:
            print("turning light on")
        self.light.off()
        self.led_state = True

    def turn_light_off(self):
        if self.debug:
            print("turning light off")
        self.light.on()
        self.led_state = False

    def turn_inpump_on(self):
        if self.debug:
            print("turning inpump on")
        self.inpump.off()
        self.inpump_state = True

    def turn_inpump_off(self):
        if self.debug:
            print("turning inpump off")
        self.inpump.on()
        self.inpump_state = False

    def turn_outpump_on(self):
        if self.debug:
            print("turning outpump on")
        self.outpump.off()
        self.outpump_state = True

    def turn_outpump_off(self):
        if self.debug:
            print("turning outpump off")
        self.outpump.on()
        self.outpump_state = False

    def cycle_inpump(self):
        if self.inpump_state:
            self.turn_inpump_off()
        else:
            self.turn_inpump_on()

    def cycle_outpump(self):
        if self.outpump_state:
            self.turn_outpump_off()
        else:
            self.turn_outpump_on()

    def send_text(self, msg):
        if self.text:
            self.twilio_client.messages.create(
                to=f"+1{self.twilio_to_number}",
                from_=f"+1{self.twilio_from_number}",
                body=msg
            )
        else:
            print(msg)

    def send_led_on_text(self):
        if not self.sent_led_on_text:
            self.send_text("turning on LED")
            self.sent_led_on_text = True

    def send_led_off_text(self):
        if not self.sent_led_off_text:
            self.send_text("turning off LED")
            self.sent_led_off_text = True

    def send_outpump_on_text(self):
        if not self.sent_outpump_on_text:
            self.send_text("turning on outpump")
            self.sent_outpump_on_text = True

    def send_outpump_off_text(self):
        if not self.sent_outpump_off_text:
            self.send_text("turning off outpump")
            self.sent_outpump_off_text = True

    def send_alert_text(self, alert, wait_time_seconds):
        if (
                dt.datetime.now() - self.previous_alert_times.get(alert, dt.datetime(2000, 1, 1))
                >= dt.timedelta(seconds=wait_time_seconds)
        ):
            self.send_text(alert)
        self.previous_alert_times[alert] = dt.datetime.now()

    def water_level_too_high(self):
        water_level_too_high = self.water_level_sensor.value == 0
        if self.debug:
            print(f"water too high: {water_level_too_high}")
        return water_level_too_high

    def reset_day(self):
        self.day = dt.datetime.today().day
        self.sent_led_on_text = False
        self.sent_led_off_text = False
        self.sent_outpump_on_text = False
        self.sent_outpump_off_text = False

    def step(self):
        day = dt.datetime.today().day
        if day > self.day:
            self.reset_day()

        hour = dt.datetime.today().hour
        second = dt.datetime.today().second

        temp = self.si7021.get_temp('F')
        if second == 0 or self.debug:
            print("TEMP F : ", temp)
        if temp is not None and (temp < self.low_temp_threshold or temp > self.high_temp_threshold):
            self.send_alert_text(f"Temperature alert: {round(temp)} Degrees F", self.alert_wait_time_seconds)
        humidity = self.si7021.get_humidity()
        if second == 0 or self.debug:
            print("HUMIDITY: ", humidity)
        if humidity is not None and (humidity < self.low_humidity_threshold or humidity > self.high_humidity_threshold):
            self.send_alert_text(f"Humidity alert: {round(humidity)}%", self.alert_wait_time_seconds)


        if hour >= self.led_start_hour and hour <= self.led_end_hour:
            self.turn_light_on()
            self.send_led_on_text()
        else:
            self.turn_light_off()
            self.send_led_off_text()

        if self.water_level_too_high():
            self.turn_outpump_on()
            self.send_outpump_on_text()
        else:
            self.turn_outpump_off()
            self.send_outpump_off_text()

        if second <= self.inpump_on_seconds:
            self.turn_inpump_on()
        else:
            self.turn_inpump_off()

        time.sleep(1)
        sys.stdout.flush()
    def run(self):
        while True:
            self.step()

def main():
    fire.Fire(AeroController)
