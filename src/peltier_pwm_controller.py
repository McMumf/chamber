
import RPi.GPIO as GPIO
from OperatingMode import OperatingMode

"""
Individual Control for TEC1/Peltier

MD10C R3 to GPIO Wiring
  - GND -> GND
  - PWM -> 19
  - DIR -> 23
"""

class PeltierPwmController:

    def __init__(self, pwm_gpio_pin = 19, dir_pin = 23):
        """
        Constructor.

        Parameters
        ----------
        pwm_gpio_pin: PWM control pin for the peltier
            Default is GPIO Pin 19, the physical pin number is 35
        dir_pin: direction pin
            Default is 23
        """
        self.pwm_gpio_pin_num = pwm_gpio_pin
        self.dir_pin = dir_pin

    def change_heating_direction(self, operating_mode: OperatingMode):
        """
        Set the direction of the peltier based on operating mode.

        Parameters
        ----------
        operating_mode : OperatingMode
            The current operating mode
        """
        if(operating_mode == OperatingMode.HEATING):
            GPIO.output(self.dir_pin, False)
        else:
            GPIO.output(self.dir_pin, True)

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
        Configure GPIO for pwm and start it
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pwm_gpio_pin_num, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.output(self.dir_pin, False)
        self.pwm = GPIO.PWM(self.pwm_gpio_pin_num, 60)
        self.pwm.start(0.0)


    def cleanup(self):
        """
        Safe shutdown of pwm and gpio
        """
        self.pwm.ChangeDutyCycle(0)
        self.pwm.stop()
