from display_controller import DisplayController
from ds18b20_controller import Ds18b20Controller
from fan_pwm_controller import FanPwmController
from peltier_pwm_controller import PeltierPwmController
import RPi.GPIO as GPIO
import signal
import sys

from enum import Enum

stop = False

class OperatingMode(Enum):
    HEATING = 1
    COOLING = 2
    RESTING = 3

def signal_handler(signum, frame):
    print('Handling signal')
    global stop
    stop = True

def increase_temp_setpoint():
    print('Inreasing setpoint')

def decrease_temp_setpoint():
    print('Decreasing setpoint')

def main():
    print("Hello World!")

    display_controller = DisplayController()
    ds18b20_controller = Ds18b20Controller()
    fan_pwm = FanPwmController()
    peltier_pwm = PeltierPwmController()

    # Initialize
    display_controller.init_display()

    _, fahrenheit = ds18b20_controller.read_temp()

    target_temp_f = 75
    flip_flop = 0
    loop_count = 0
    mode = OperatingMode.REST

    while (not stop):
        if (abs(fahrenheit - target_temp_f) > 1 or mode != OperatingMode.RESTING):
            if (fahrenheit > target_temp_f):
                if (mode == OperatingMode.HEATING):
                    flip_flop += 1
                else:
                    mode = OperatingMode.COOLING
            else:
                if (mode == OperatingMode.COOLING):
                    flip_flop += 1
                else:
                    mode == OperatingMode.HEATING

        if (flip_flop > 0 or mode == OperatingMode.RESTING):
            # Disable fans and Peltier near target temp.
            fan_pwm.set_duty_cycle(0)
            peltier_pwm.set_duty_cycle(0)
            flip_flop = 0
        else:
            fan_pwm.set_duty_cycle(100)
            peltier_pwm.set_duty_cycle(100)

        # Display and print temperature at reduced loop rate.
        if (loop_count == 0 or loop_count % 10 == 0):
            updated_text = f"Temp: {str(round(fahrenheit)) + chr(247)}F | {mode}\n     ({str(target_temp_f) + chr(247)}F)"
            display_controller.draw_text(updated_text)

        print(f"Target: {target_temp_f}")
        print(f"Temp: {fahrenheit}")
        print(f"Mode: {mode}")
        print("=============")

        loop_count += 1

    fan_pwm.cleanup()
    peltier_pwm.cleanup()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
