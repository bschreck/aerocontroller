import datetime as dt
import sys
# switch is 8/gpio14

from .SI7021 import SI7021
from gpiozero import LED
import time
from twilio.rest import Client as TwilioClient
import math
from dotenv import load_dotenv
import os

class AeroController:
    def __init__(self, env_path):
        self.env_path = env_path
        load_dotenv(dotenv_path=self.env_path)
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

        self.si7021 = SI7021()
        self.light = LED('BOARD11')
        self.inpump = LED('BOARD18')
        self.outpump = LED('BOARD16')
        self.inpump_state = False
        self.outpump_state = False

    def turn_light_on(self):
        self.light.off()

    def turn_light_off(self):
        self.light.on()

    def turn_inpump_on(self):
        self.inpump.off()

    def turn_inpump_off(self):
        self.inpump.on()

    def turn_outpump_on(self):
        self.outpump.on()

    def turn_outpump_off(self):
        self.outpump.off()

    def cycle_inpump(self):
        if self.inpump_state:
            self.turn_inpump_off()
        else:
            self.turn_inpump_oon()

    def cycle_outpump(self):
        if self.inpump_state:
            self.outpump.off()()
        else:
            self.outpump.on()

    def send_text(self, msg):
        self.twilio_client.messages.create(
            to=f"+1{self.twilio_to_number}",
            from_=f"+1{self.twilio_from_number}",
            body=msg
        )

    def run(self):
        temp = self.si7021.get_temp('F')
        print("TEMP F : ", temp)
        if temp < self.low_temp_threshold or temp > self.high_temp_threshold:
            self.send_text(f"Temperature alert: {round(temp)}%")
        humidity = self.si7021.get_humidity()
        print("HUMIDITY: ", humidity)
        if humidity < self.low_humidity_threshold or humidity > self.high_humidity_threshold:
            self.send_text(f"Humidity alert: {round(humidity)}%")

        hour = dt.datetime.today().hour

        print("HOUR = ", hour)
        if hour >= self.led_start_hour and hour <= self.led_end_hour:
            self.turn_light_on()
            self.send_text("turning on LED")
        else:
            self.turn_light_off()
            self.send_text("turning off LED")

        if hour >= self.outpump_start_hour and hour <= self.outpump_end_hour:
            self.turn_outpump_on()
            self.send_text("turning on outpump")
        else:
            self.turn_outpump_off()
            self.send_text("turning off outpump")

        second = dt.datetime.today().second
        if second <= self.inpump_on_seconds:
            self.turn_inpump_on()
        else:
            self.turn_inpump_off()

        time.sleep(1)
        sys.stdout.flush()

if __name__ == '__main__':
    controller = AeroController('.env')
    while True:
        controller.run()
