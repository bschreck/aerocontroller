# from gpiozero import LED
# import time


# class Relay
    # On = 1
    # Off = 0
    # relay_pins = [29, 31, 33, 35]


    # def __init__(self):
        # GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BOARD)
        # for pin in self.relay_pins:
            # GPIO.setup(pin, GPIO.OUT)
        # self.objects = {}

    # def set_state(self, pin, state, test=False):
        # '''Change state if different'''
        # msg = "{}, {}, {}".format("Current ", state, GPIO.input(pin))
        # self.logger.debug(msg)
        # if state == ON and not GPIO.input(pin):
            # self.set_on(pin)
            # msg = "{} {} {}".format("Pin:", pin, " On")
            # self.logger.debug(msg)
        # elif state == OFF and GPIO.input(pin):
            # self.set_off(pin)
            # msg = "{} {} {}".format("Pin:", pin, " Off")
            # self.logger.debug(msg)
        # else:
            # msg = "{} {} {}".format("Pin:", pin, " No Change")
            # self.logger.debug(msg)

    # def get_state(self, pin):
        # return GPIO.input(pin)

    # def set_off(self, pin, test=False):
        # GPIO.output(pin, GPIO.LOW)

    # def set_on(self, pin, test=False):
        # GPIO.output(pin, GPIO.HIGH)

    # def add_object(self, name, pin):
        # self.objects[name] = RelayObject(name, self, self.objects[pin])
        # return self.objects[name]

    # def __getattr__(self, name):
        # obj = self.objects.get(name, None)
        # if obj:
            # return obj
        # return super().__getattr__(name)

    # def __getitem__(self, name):
        # obj = self.objects.get(name, None)
        # if obj:
            # return obj
        # return super().__getitem__(name)


# class RelayObject:
    # def __init__(self, name, relay, pin):
        # self.name = name
        # self.pin = pin

    # def __repr__(self):
        # return f"{name}RelayObject: state = {self.state}"

    # @property
    # def state(self):
        # return self.relay.get_state(self.pin)

    # def set_on(self):
        # self.relay.set_on(self.pin)

    # def set_off(self):
        # self.relay.set_off(self.pin)
