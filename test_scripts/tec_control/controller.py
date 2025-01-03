
import RPi.GPIO as GPIO
import time

"""
Individual Control for TEC1/Peltier

MD10C R3 to GPIO Wiring
  - GND -> GND
  - PWM -> 19
  - DIR -> 23
"""

dir_pin = 23 # The direction of the tec
pwm_gpio_pin_num = 19 # this will be GPIO Pin 19, the physical pin number is 35

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pwm_gpio_pin_num, GPIO.OUT)
    GPIO.setup(dir_pin, GPIO.OUT) o

setup()

pwm = GPIO.PWM(pwm_gpio_pin_num, 60)
pwm.start(0)

time.sleep(2)

try:
    while True:
        pwm.ChangeDutyCycle(100)
        print('Duty Cycle: 100')
        time.sleep(5)
        pwm.ChangeDutyCycle(0)
        print('Duty Cycle: 0')
        time.sleep(30)

except KeyboardInterrupt:
    pass

pwm.ChangeDutyCycle(0)
pwm.stop()
GPIO.cleanup()
