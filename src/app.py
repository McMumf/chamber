from OperatingMode import OperatingMode
from display_controller import DisplayController
from ds18b20_controller import Ds18b20Controller
from fan_pwm_controller import FanPwmController
from peltier_pwm_controller import PeltierPwmController
import RPi.GPIO as GPIO
import signal
import sys

stop = False

display_controller = DisplayController()
ds18b20_controller = Ds18b20Controller()
fan_pwm = FanPwmController()
peltier_pwm = PeltierPwmController()

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

    target_temp_f = 75
    flip_flop = 0
    loop_count = 0
    mode = OperatingMode.RESTING

    # Initialize
    display_controller.init_display()
    fan_pwm.setup()
    peltier_pwm.setup()

    while (not stop):
        _, fahrenheit = ds18b20_controller.read_temp()
        if (abs(fahrenheit - target_temp_f) > 1 or mode != OperatingMode.RESTING):
            if (fahrenheit > target_temp_f):
                if (mode == OperatingMode.HEATING):
                    print('Mode is heating, flip flopping')
                    flip_flop += 1
                else:
                    print('Time to cool')
                    mode = OperatingMode.COOLING
            else:
                if (mode == OperatingMode.COOLING):
                    print('time to heatup')
                    flip_flop += 1
                else:
                    print('Changing mode to heating')
                    mode = OperatingMode.HEATING

        if (flip_flop > 0 or mode == OperatingMode.RESTING):
            # Disable fans and Peltier near target temp.
            print('Disabling fans')
            fan_pwm.set_duty_cycle(0)
            print('Disabling peltier')
            peltier_pwm.set_duty_cycle(0)
            flip_flop = 0
        else:
            print('Enabling fans')
            fan_pwm.set_duty_cycle(100)
            peltier_pwm.set_duty_cycle(100)
            peltier_pwm.change_heating_direction(mode)

        # Display and print temperature at reduced loop rate.
        if (loop_count == 0 or loop_count % 10 == 0):
            display_controller.clear_display()
            updated_text = f"Temp: {str(round(fahrenheit)) + chr(176)}F | {str(mode)}\n Target Temp: {str(target_temp_f) + chr(176)}F"
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
    try:
        main()
    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            print(e)
        fan_pwm.set_duty_cycle(0)
        fan_pwm.cleanup()
        peltier_pwm.set_duty_cycle(0)
        peltier_pwm.cleanup()
        display_controller.cleanup()
        GPIO.cleanup()
