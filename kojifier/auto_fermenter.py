import time
from pathlib import Path
import sys
import os
import logging
import fire

from dotenv import load_dotenv
from kojifier import utils
from kojifier.pwm import PWM
from kojifier.logging import get_logger


logger = get_logger(__name__)





class AutoFermenter:
    def __init__(self,
                 config=None,
                 soak_time=60*60*12,
                 pre_steam_drain_time=60*10,
                 steam_time=60*60,
                 cool_time=60*10,
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
        self.pre_steam_drain_time = pre_steam_drain_time
        self.steam_time = steam_time
        self.cool_time = cool_time
        self.drain_time = drain_time
        self.dry_time = dry_time
        self.wait_for_human_input_time = wait_for_human_input_time
        self.incubate_time = incubate_time
        self.incubate_temp = incubate_temp
        self.slack = slack
        self.interval_time =  interval_time
        self.unit = unit
        self.temp_sensor = utils.W1SensorWrapper()
        self.fan = utils.LEDReverseWrapper(5)
        self.plate = PWM(6)
        self.in_vent = utils.LEDReverseWrapper(19)
        self.out_vent = utils.LEDReverseWrapper(13)
        self.drain = utils.LEDReverseWrapper(26)

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
        else:
            self.in_vent.off()
            self.out_vent.off()
            self.fan.off()

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
        logger.info("Soaking")
        time.sleep(self.soak_time)
        logger.info("Draining")
        self.cool(with_vent=False, with_drain=True)
        time.sleep(self.pre_steam_drain_time)
        logger.info("Heating")
        self.heat()
        time.sleep(self.steam_time)
        logger.info("Cooling")
        self.cool(with_vent=False, with_drain=False)
        time.sleep(self.cool_time)
        logger.info("Draining")
        self.cool(with_vent=False, with_drain=True)
        time.sleep(self.drain_time)
        logger.info("Drying")
        self.cool(with_vent=True, with_drain=True)
        time.sleep(self.dry_time)
        self.cool(with_vent=False, with_drain=False)
        alerted = False
        logger.info("Waiting for correct incubate temperature")
        while True:
            target_temp = self.incubate_adjust()
            if not alerted and target_temp:
                logger.info("At target temperature")
                self.alert_target_temp()
                alerted = True
                logger.info("Waiting for human input")
                time.sleep(self.wait_for_human_input_time)
                start_incubate_time = time.time()
                logger.info("Starting to incubate")
            elif alerted and time.time() - start_incubate_time > self.incubate_time:
                logger.info("Finished incubating")
                break
            time.sleep(self.interval_time)
        self.alert_done()


def cli():
    fire.Fire(AutoFermenter)
