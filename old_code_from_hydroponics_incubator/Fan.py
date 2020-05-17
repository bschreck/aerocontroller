"""
# Acuator for the exhaust fan
# Author: Howard Webb
# Date: 2/15/2017
"""

from env import env
from Relay import *
import time
from LogUtil import get_logger
from CouchUtil import saveList

class Fan(object):
    """Code associated with the exhaust fan"""

    relay = None
    target_temp = 0

    def __init__(self, pin, relay):
        self.logger = get_logger("Fan")
        self.pin = pin
        self.relay = relay

    def set_on(self):
        self.relay.set_state(self.pin, self.relay.On)

    def set_off(self):
        self.relay.set_state(self.pin, self.relay.Off)

    def get_state(self):
        return self.relay.get_state(self.pin)

    def log_state(self, value, test=False):
        """Send state change to database
           Args:
               value: state change
               test: flag for testing
           Returns:
               None
           Raises:
               None
        """
        status_qualifier = 'Success'
        if test:
            status_qualifier = 'Test'
        saveList(['State_Change', '', 'Side', 'Fan', 'State', value, 'state', 'Fan', status_qualifier, ''])

def test():
    """Self test
           Args:
               None
           Returns:
               None
           Raises:
               None
    """
    fan = Fan()
    print "Test"
    print "State: ", fan.relay.get_state(fan.fan_relay)
    print "Turn Fan On"
    fan.set_fan_on()
    print "State: ", fan.relay.get_state(fan.fan_relay)
    time.sleep(2)

    print "Turn Fan Off"
    fan.set_fan_off()
    print "State: ", fan.relay.get_state(fan.fan_relay)
    time.sleep(2)

    print "Adj 45"
    fan.adjust(45, True)
    print "State: ", fan.relay.get_state(fan.fan_relay)

    print "Adj 45"
    fan.adjust(45, True)
    print "State: ", fan.relay.get_state(fan.fan_relay)

    print "Adj 10"
    fan.adjust(10, True)
    print "State: ", fan.relay.get_state(fan.fan_relay)

    print "Adj 45"
    fan.adjust(45, True)
    print "State: ", fan.relay.get_state(fan.fan_relay)
    print "Done"

if __name__ == "__main__":
    test()


