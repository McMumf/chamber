
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

class PeltierPwmController:

    def __init__(self, pwm_gpio_pin = 18, dir_pin = 23):
        pwm_gpio_pin_num = pwm_gpio_pin
        self.setup()
        self.pwm = GPIO.PWM(pwm_gpio_pin_num, 60)
        self.dir_pin = dir_pin

    def set_duty_cycle(self, duty_cycle: float):
        """
        Sets the duty cycle for the pwm.

        Parameters
        ----------
        duty_cycle : float
            The percentage of time that the PWM is on during a complete cycle
        """
        self.pwm.ChangeDutyCycle(duty_cycle)

    def setup(self):
        """
        Configure GPIO for pwm
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pwm_gpio_pin_num, GPIO.OUT)
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.output(dir_pin, False)

    def cleanup(self):
        """
        Safe shutdown of pwm and gpio
        """
        self.pwm.ChangeDutyCycle(0)
        self.pwm.stop()
