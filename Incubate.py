"""
# Author: Howard Webb
# Data: 7/25/2017
# Thermostat controller that reads the temperature sensor and adjusts the exhaust fan

"""
from Fan import Fan
from SI7021 import SI7021

# TODO: turn out fan and top fan on if humidity too high
# and reverse otherwise
# turn all in/out on if heat too high
# turn top off if humidity too low unless in "cooling" state
def adjust_thermostat(target_temp, light, fan, slack=1):
    temp_sensor = SI7021()
    temp = temp_sensor.get_tempC()
    l = Light()
    l.set_on()
    f = Fan()

    fan1_state, fan2_state = fan.relay.get_state(self.fan_relay)
    light_state = light.get_state()
    msg = "{} {} {} {} {} {}".format(
            "Temp:", temp, 
            " Target Temp:", target_temp, 
            " Fan State:", fan_state,
            " Light state:", light_state)
    self.logger.info(msg)
    if temp > (target_temp + slack):
        if not fan1_state or not fan2_state:
            fan.set_fan_on()
            self.logger.debug("Turning fan on")
        if light_state:
            light.set_off()
            self.logger.debug("Turning light off")
        self.log_state("Cooling")

    elif temp <= (target_temp - slack):
        if fan_state:
        if fan1_state or fan2_state:
            self.set_fan_off()
            self.logger.debug("Turning fan off")
        if not light_state:
            light.set_on()
            self.logger.debug("Turning light on")
        self.log_state("Heating")
    else:
        self.logger.debug("No change to state")

    fan = Fan()
    fan.adjust(temp, test)

def test():
    """Self test
           Args:
               None
           Returns:
               None
           Raises:
               None
    """
    print "Test"
    adjust_thermostat(40, True)
    print "Adjust Thermostat 40"
    adjust_thermostat(20, True)
    print "Adjust Thermostat 20"
    adjust_thermostat(None, True)
    print "Adjust Thermostat None"

if __name__ == "__main__":
    adjust_thermostat()



