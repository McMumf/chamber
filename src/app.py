from OperatingMode import OperatingMode
from display_controller import DisplayController
from ds18b20_controller import Ds18b20Controller
from fan_pwm_controller import FanPwmController
from peltier_pwm_controller import PeltierPwmController
import RPi.GPIO as GPIO

stop = False

display_controller = DisplayController()
ds18b20_controller = Ds18b20Controller()
fan_pwm = FanPwmController()
peltier_pwm = PeltierPwmController()
target_temp_f = 75

def decrease_target_temp_callback(channel):
    print('Decreasing target temp')
    global target_temp_f
    target_temp_f -= 1

def increase_target__temp_callback(channel):
    print('Increasing target temp')
    global target_temp_f
    target_temp_f += 1

def signal_handler(signum, frame):
    print('Handling signal')
    global stop
    stop = True

def main():
    print("Hello World!")

    global target_temp_f
    target_temp_f = 75
    flip_flop = 0
    loop_count = 0
    mode = OperatingMode.RESTING

    GPIO.setwarnings(False)

    # Initialize
    display_controller.init_display()
    fan_pwm.setup()
    peltier_pwm.setup()

    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.add_event_detect(20,GPIO.RISING,callback=decrease_target_temp_callback)
    GPIO.add_event_detect(21,GPIO.RISING,callback=increase_target__temp_callback)

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

            if fahrenheit < 83:
                peltier_pwm.set_duty_cycle(100)
                peltier_pwm.change_heating_direction(mode)
            else:
                peltier_pwm.set_duty_cycle(0)

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
        print(e)
        fan_pwm.set_duty_cycle(0)
        fan_pwm.cleanup()
        peltier_pwm.set_duty_cycle(0)
        peltier_pwm.cleanup()
        display_controller.cleanup()
        GPIO.cleanup()
