
import os

import signal
import sys
import RPi.GPIO as GPIO

pin = 26

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.setwarnings(False)

def fan_on():
    setPin(True)

def fan_off():
    setPin(False)


