from relay import Relay
from SI7021 import SI7021


def incubate(target_temp, target_humidity, slack=1):
    temp_sensor = SI7021()
    temp = temp_sensor.get_tempC()
    humidity = temp_sensor.get_humidity()
    relay = Relay()
    on = relay.On
    off = relay.Off
    light = relay.add_object("Light", 29)
    overhead_fan = relay.add_object("OverheadFan", 31)
    in_fan = relay.add_object("InFan", 33)
    out_fan = relay.add_object("OutFan", 35)

    print("Current State:")
    print(f"Target Temp = {target_temp}")
    print(f"Current Temp = {temp}")
    print(f"Target Humidity = {target_humidity}")
    print(f"Current Humidity = {humidity}")
    print(f"Light state = {light.state}")
    print(f"Overhead fan state = {overhead_fan.state}")
    print(f"In fan state = {in_fan.state}")
    print(f"Out fan state = {out_fan.state}")
    if temp > (target_temp + slack):
        print("Setting state to cooling")
        in_fan.set_on()
        out_fan.set_on()
        light.set_off()
    elif temp < (target_temp - slack):
        print("Setting state to heating")
        in_fan.set_off()
        out_fan.set_off()
        light.set_on()
    else:
        print("No temperature action taken")
    if humidity > (target_humidity + slack):
        print("Setting state to drying")
        out_fan.set_on()
        overhead_fan.set_on()
    elif humidity < (target_humidity - slack):
        print("Setting state to moistening")
        out_fan.set_off()
        overhead_fan.set_off()
    else:
        print("No humidity action taken")


if __name__ == '__main__':
    incubate()
