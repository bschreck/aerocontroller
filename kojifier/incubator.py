# from relay import Relay
from .SI7021 import SI7021
from gpiozero import LED
# from signal import pause
import fire


def adjust(temp=25, humidity=90, slack=1):
    target_temp = temp
    target_humidity = humidity
    # temp_sensor = SI7021()
    # temp = temp_sensor.get_tempC()
    temp = 20
    # humidity = temp_sensor.get_humidity()
    humidity = 85


    print("Current State:")
    print(f"Target Temp = {target_temp}")
    print(f"Current Temp = {temp}")
    print(f"Target Humidity = {target_humidity}")
    print(f"Current Humidity = {humidity}")

    light = LED('BOARD29')
    overhead_fan = LED('BOARD31')
    in_fan = LED('BOARD33')
    out_fan = LED('BOARD35')
    if temp > (target_temp + slack):
        print("Setting state to cooling")
        in_fan.on()
        out_fan.on()
        light.off()
    elif temp < (target_temp - slack):
        print("Setting state to heating")
        in_fan.off()
        out_fan.off()
        light.on()
    else:
        print("No temperature action taken")
    if humidity > (target_humidity + slack):
        print("Setting state to drying")
        out_fan.on()
        overhead_fan.on()
    elif humidity < (target_humidity - slack):
        print("Setting state to moistening")
        out_fan.off()
        overhead_fan.off()
    else:
        print("No humidity action taken")

    # signal.pause()


def main():
      fire.Fire(adjust)
