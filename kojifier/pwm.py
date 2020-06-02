from RPi.GPIO import GPIO
from kojifier.logging import get_logger
from kojifier import utils


logger = get_logger(__name__)


class PWM:
    def __init__(self, pin, max_hz=10):
        self.pin = pin
        self.max_hz = max_hz
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
        self.obj = None

    def power_to_freq(self, power):
        return power * self.max_hz

    def set_power(self, power):
        self.obj = GPIO.PWM(self.pin, self.power_to_freq(power))
        self.obj.start(1)

    def off(self):
        if self.obj:
            self.obj.stop()
            GPIO.cleanup()

