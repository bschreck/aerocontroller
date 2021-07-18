import time
import datetime
from pathlib import Path
import sys
import os
import logging
import fire

from dotenv import load_dotenv
from kojifier import utils
from kojifier.utils import W1SensorWrapper
from kojifier.pwm import PWM
from kojifier.logging import get_logger
from simple_pid import PID
import pandas as pd


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
                 interval_time=0.5,
                 unit='F',
                 phone_number=None,
                 env_path=os.path.expanduser('~/.env'),
                 pwm_freq=2,
                 pid_Kp=1.0,
                 pid_Ki=0.1,
                 pid_Kd=0.05,
                 pid_update_tuning_time=10,
                 checkpoint_length=10,
                 history_file=os.path.expanduser('~/.auto_fermenter_history')
                 ):
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
        self.temp_sensor = W1SensorWrapper(self)
        self.fan = utils.LEDReverseWrapper(5)
        self.plate = PWM(6)
        self.in_vent = utils.LEDReverseWrapper(19)
        self.out_vent = utils.LEDReverseWrapper(13)
        self.drain = utils.LEDReverseWrapper(26)

        load_dotenv(dotenv_path=env_path)
        self.twilio_sid = os.environ.get("TWILIO_SID")
        self.twilio_token = os.environ.get("TWILIO_TOKEN")
        self.twilio_from_number = os.environ.get("TWILIO_FROM_NUMBER")
        self.phone_number = phone_number

        self.pwm_freq = pwm_freq
        self.pid_Kp = pid_Kp
        self.pid_Ki = pid_Ki
        self.pid_Kd = pid_Kd
        self.pid_update_tuning_time = pid_update_tuning_time

        self.checkpoint_length = checkpoint_length
        self.history_file = history_file

        self.config_file = config
        if self.config_file:
            for k, v in utils.load_config(self.config_file).items():
                setattr(self, k, v)

        if self.phone_number and self.twilio_sid and self.twilio_token:
            from twilio.rest import Client
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)

        self.pid = PID(self.pid_Kp, self.pid_Ki, self.pid_Kd,
                       setpoint=self.incubate_temp)
        self.pid.output_limits = (0, 100)
        # self.pid.sample_time = self.interval_time
        self.history = {
            'power': [],
            'temp': [],
            'time': [],
        }

    def log_history(self, power):
        self.history['power'].append(power)
        self.history['temp'].append(self.temp)
        self.history['time'].append(datetime.datetime.now())

    def adjust_hot_plate(self, power):
        self.log_history(power)
        self.plate.set_duty_cycle(power)

    def heat(self):
        self.log_history(100)
        self.plate.set_duty_cycle(100)
        self.fan.off()
        self.in_vent.off()
        self.out_vent.off()
        self.drain.off()

    def cool(self, with_vent=False, with_drain=False):
        self.log_history(0)
        self.plate.set_duty_cycle(0)
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

    @property
    def temp(self):
        return self.temp_sensor.get_temp(self.unit)

    def incubate_adjust(self):
        if self.temp is None:
            logger.info("Unknown current temp")
            sys.stdout.flush()
            return False
        logger.info("Current State:")
        logger.info(f"Target Temp = {self.incubate_temp}")
        logger.info(f"Current Temp = {self.temp}")
        self.new_hot_plate_power = self.pid(self.temp)
        self.adjust_hot_plate(self.new_hot_plate_power)
        sys.stdout.flush()
        if not self.too_hot and not self.too_cold:
            return True
        return False

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
        self.save_history()
        self.previous_checkpoint = time.time()
        self.last_pid_update = time.time()
        while True:
            at_target_temp = self.incubate_adjust()
            if not alerted and at_target_temp:
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
            if time.time() - self.previous_checkpoint > self.checkpoint_length:
                self.save_history()
                self.previous_checkpoint = time.time()
            if time.time() - self.last_pid_update > self.pid_update_tuning_time:
                self.set_pid()
                self.last_pid_update = time.time()

        self.alert_done()
        self.save_history()
    def save_history(self):
        pd.DataFrame(self.history).to_csv(self.history_file, index=False)

    def set_pid(self):
        try:
            if self.config:
                config = utils.load_config(config)
                tunings = (config['pid_Kp'], config['pid_Ki'], config['pid_Kd'])
                setpoint = config['incubate_temp']
        except Exception as e:
            print("unable to load new config")
            return
        if tunings != self.pid.tunings:
            print(f"setting tunings to {tunings}")
            try:
                self.pid.tunings = tuple([float(x) for x in tunings])
            except (ValueError, TypeError):
                print("Unable to set tunings")
                return
        if setpoint != self.pid.setpoint:
            print(f"setting setpoint to {setpoint}")
            try:
                pid.setpoint = float(setpoint)
            except (ValueError, TypeError):
                print("Unable to set setpoint")
        return tunings, setpoint


def cli():
    fire.Fire(AutoFermenter)
