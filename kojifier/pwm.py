import RPi.GPIO as GPIO
from kojifier.logging import get_logger
from kojifier import utils


logger = get_logger(__name__)


class PWM:
    def __init__(self, pin, freq=1, reverse=True):
        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BCM)
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
        self.obj = GPIO.PWM(self.pin, self.freq)
        self.reverse = reverse
        if self.reverse:
            self.obj.start(1)
        else:
            self.obj.start(100)

    def set_duty_cycle(self, dc):
        if self.reverse:
            dc = 100 - dc
        self.obj.ChangeDutyCycle(dc)

    def off(self):
        if self.obj:
            self.obj.stop()
            GPIO.cleanup()

