
import RPi.GPIO as GPIO
import time

"""
NT07-115X Wiring
    - Pins
        - 1: Black
        - 2: Red
        - 3: Yellow
        - 4: Blue
    - Function
        - 1: Ground
        - 2: +12v/5v
        - 3: Tach/Signal/Sense
        - 4: Control/PWM
"""

pwm_pin_num = 12

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pwm_pin_num, GPIO.OUT)

setup()

pwm = GPIO.PWM(pwm_pin_num, 25000)
pwm.start(0)

time.sleep(2)

try:
    while True:
        pwm.ChangeDutyCycle(100)
        print('Duty Cycle: 100')
        time.sleep(5)
        pwm.ChangeDutyCycle(50)
        print('Duty Cycle: 50')
        time.sleep(5)
        pwm.ChangeDutyCycle(0)
        print('Duty Cycle: 0')
        time.sleep(5)

except KeyboardInterrupt:
    pass

pwm.ChangeDutyCycle(0)
pwm.stop()
GPIO.cleanup()
