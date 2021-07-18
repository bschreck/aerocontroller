import datetime as dt
import sys
# switch is 8/gpio14

from .SI7021 import SI7021
from gpiozero import LED
import time
from twilio.rest import Client as TwilioClient
import math

load_dotenv(dotenv_path=env_path)
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")
TWILIO_TO_NUMBER = os.environ.get("TWILIO_TO_NUMBER")
TWILIO_CLIENT = TwilioClient(twilio_sid, twilio_token)
LOW_HUMIDITY_THRESHOLD = int(os.environ.get("LOW_HUMIDITY_THRESHOLD"))
HIGH_HUMIDITY_THRESHOLD = int(os.environ.get("LOW_HUMIDITY_THRESHOLD"))
LOW_TEMP_THRESHOLD = int(os.environ.get("LOW_TEMP_THRESHOLD"))
HIGH_TEMP_THRESHOLD = int(os.environ.get("HIGH_TEMP_THRESHOLD"))
LED_START_HOUR = int(os.environ.get("LED_START_HOUR"))
LED_END_HOUR = int(os.environ.get("LED_END_HOUR"))
OUTPUMP_START_HOUR_START_HOUR = int(os.environ.get("OUTPUMP_START_HOUR"))
OUTPUMP_END_HOUR = int(os.environ.get("OUTPUMP_END_HOUR"))
INPUMP_ON_SECONDS = int(os.environ.get("INPUMP_ON_SECONDS"))

SI7021 = SI7021()
LIGHT = LED('BOARD11')
INPUMP = LED('BOARD18')
OUTPUMP = LED('BOARD16')

def turn_light_on():
    LIGHT.off()
def turn_light_off():
    LIGHT.on()
def turn_inpump_on():
    INPUMP.off()
def turn_inpump_off():
    INPUMP.on()
def cycle_inpump():
    if INPUMP_STATE:
        turn_inpump_off()
    else:
        turn_inpump_oon()
def cycle_outpump():
    if INPUMP_STATE:
        OUTPUMP.off()()
    else:
        OUTPUMP.on()


def send_text(msg):
    twilio_client.messages.create(
        to=f"+1{twilio_to_number}",
        from_=f"+1{twilio_from_number}",
        body=msg
    )

while True:
    temp = SI7021.get_temp('F')
    print("TEMP F : ", temp)
    if temp < LOW_TEMP_THRESHOLD or temp > HIGH_TEMP_THRESHOLD:
        send_text(f"Temperature alert: {math.round(temp)}%")
    humidity = SI7021.get_humidity()
    print("HUMIDITY: ", humidity)
    if humidity < LOW_HUMIDITY_THRESHOLD or humidity > HIGH_HUMIDITY_THRESHOLD:
        send_text(f"Humidity alert: {math.round(humidity)}%")

    hour = dt.datetime.today().hour

    print("HOUR = ", hour)
    if hour >= LED_START_HOUR and hour <= LED_END_HOUR
        turn_light_on()
        send_text("turning on LED")
    else:
        turn_light_off()
        send_text("turning off LED")

    if hour >= OUTPUMP_START_HOUR and hour <= OUTPUMP_END_HOUR:
        turn_outpump_on()
        send_text("turning on outpump")
    else:
        turn_outpump_off()
        send_text("turning off outpump")

    second = dt.datetime.today().seoond
    if second <= INPUMP_ON_SECONDS:
        turn_inpump_on()
    else:
        turn_inpump_off()

    time.sleep(1)
    sys.stdout.flush()
