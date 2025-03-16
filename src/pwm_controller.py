import RPi.GPIO as GPIO
import time

class PwmController:
    """
    Class to control Pulse Width Modulation (PWM) for the fans and peltier.

    NT07-115X (fan) Wiring
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

    def __init__(self, pwm_gpio_pin = 18):
        pwm_gpio_pin_num = pwm_gpio_pin # this will be GPIO Pin 18, the physical pin number is 12
        self.pwm = GPIO.PWM(pwm_gpio_pin_num, 25000)

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
        GPIO.setup(self.pwm_gpio_pin_num, GPIO.OUT)
        self.pwm.start(0)

    def cleanup(self):
        """
        Safe shutdown of pwm and gpio
        """
        self.pwm.ChangeDutyCycle(0)
        self.pwm.stop()
        GPIO.cleanup()
