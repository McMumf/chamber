#!/usr/bin/python
from display_controller import DisplayController
from ds18b20_controller import Ds18b20Controller
from pwm_controller import PwmController

def increase_temp_setpoint():
    print('Inreasing setpoint')

def decrease_temp_setpoint():
    print('Decreasing setpoint')

def main():
    print("Hello World!")

    display_controller = DisplayController()
    ds18b20_controller = Ds18b20Controller()
    pwm_controller = PwmController()

    # Initialize
    display_controller.init_display()
    pwm_controller.setup()

    ds18b20_controller.read_temp()

if __name__ == "__main__":
    main()
