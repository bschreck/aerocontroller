import time
from pathlib import Path
import sys
import os
import logging
import fire
try:
    from w1thermsensor import W1ThermSensor
except Exception:
    pass
from gpiozero import LED
from dotenv import load_dotenv
from kojifier import utils

logger = logging.getLogger(__name__)
console = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - auto_fermenter - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
logger.setLevel(logging.INFO)


class W1SensorWrapper:
    def __init__(self):
        self.sensor = W1ThermSensor()

    def get_temp(self, unit):
        if unit == 'F':
            return self.sensor.get_temperature(W1ThermSensor.DEGREES_F)
        else:
            return self.sensor.get_temperature()


class LEDReverseWrapper:
    def __init__(self, pin):
        self.led = LED(pin)
        self.off()

    def on(self):
        self.led.off()

    def off(self):
        self.led.on()


class AutoFermenter:
    def __init__(self,
                 config=None,
                 soak_time=60*60*12,
                 steam_time=60*60,
                 drain_time=60*10,
                 dry_time=60*30,
                 wait_for_human_input_time=60*20,
                 incubate_time=60*60*36,
                 incubate_temp=88,
                 slack=1,
                 interval_time=1,
                 unit='F',
                 phone_number=None,
                 env_path=os.path.expanduser('~/.env')):
        self.soak_time = soak_time
        self.steam_time = steam_time
        self.drain_time = drain_time
        self.dry_time = dry_time
        self.wait_for_human_input_time = wait_for_human_input_time
        self.incubate_time = incubate_time
        self.incubate_temp = incubate_temp
        self.slack = slack
        self.interval_time =  interval_time
        self.unit = unit
        self.temp_sensor = W1SensorWrapper()
        self.fan = LEDReverseWrapper(5)
        self.plate = LEDReverseWrapper(6)
        self.in_vent = LEDReverseWrapper(19)
        self.out_vent = LEDReverseWrapper(13)
        self.drain = LEDReverseWrapper(26)

        load_dotenv(dotenv_path=env_path)
        self.twilio_sid =  os.environ.get("TWILIO_SID")
        self.twilio_token =  os.environ.get("TWILIO_TOKEN")
        self.twilio_from_number = os.environ.get("TWILIO_FROM_NUMBER")
        self.phone_number = phone_number

        if config:
            for k, v in utils.load_config(config).items():
                setattr(self, k, v)

        if self.phone_number and self.twilio_sid and self.twilio_token:
            from twilio.rest import Client
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)

    def heat(self):
        self.plate.on()
        self.fan.off()
        self.in_vent.off()
        self.out_vent.off()
        self.drain.off()

    def cool(self, with_vent=False, with_drain=False):
        self.plate.off()
        if with_drain:
            self.drain.on()
        else:
            self.drain.off()
        if with_vent:
            self.in_vent.on()
            self.out_vent.on()
            self.fan.on()

    @property
    def too_hot(self):
        return self.temp > (self.incubate_temp + self.slack)

    @property
    def too_cold(self):
        return self.temp < (self.incubate_temp - self.slack)

    def incubate_adjust(self):
        self.temp = self.temp_sensor.get_temp(self.unit)
        if self.temp is None:
            self.temp = 1000
        logger.info("Current State:")
        logger.info(f"Target Temp = {self.incubate_temp}")
        logger.info(f"Current Temp = {self.temp}")
        if self.too_hot:
            self.cool(with_vent=False, with_drain=False)
            return False
        elif self.too_cold:
            self.heat()
        else:
            logger.info("No temperature action taken")
        sys.stdout.flush()
        return True

    def send_text(self, msg):
        if self.twilio_client:
            self.twilio_client.messages.create(
                to=f"+1{self.phone_number}",
                from_=f"+1{self.twilio_from_number}",
                body=msg
            )
        else:
            logger.warning("No twilio client. Can't send message")

    def alert_target_temp(self):
        self.send_text(
            "AutoFermenter at target temp. "
            f"Starting to incubate in {self.wait_for_human_input_time / 60} minutes"
       )

    def alert_done(self):
        self.send_text("AutoFermenter done")

    def make_tempeh(self):
        time.sleep(self.soak_time)
        self.heat()
        time.sleep(self.steam_time)
        self.cool(with_vent=False, with_drain=True)
        time.sleep(self.drain_time)
        self.cool(with_vent=True, with_drain=True)
        time.sleep(self.dry_time)
        alerted = False
        while True:
            target_temp = self.incubate_adjust()
            if not alerted and target_temp:
                self.alert_target_temp()
                alerted = True
                time.sleep(self.wait_for_human_input_time)
                start_incubate_time = time.time()
            elif alerted and time.time() - start_incubate_time > self.incubate_time:
                break
            time.sleep(self.interval_time)
        self.alert_done()


def cli():
    fire.Fire(AutoFermenter)
