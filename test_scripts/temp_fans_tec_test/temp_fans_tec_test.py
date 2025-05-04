# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-ds18b20-python/

# Based on the Adafruit example: https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/Raspberry_Pi_DS18B20_Temperature_Sensing/code.py

import RPi.GPIO as GPIO
import os
import glob
import time
import sys

fans_pwm_gpio_pin_num = 18 # this will be GPIO Pin 18, the physical pin number is 12

tec_dir_pin = 23 # The direction of the tec
tec_pwm_gpio_pin_num = 19 # this will be GPIO Pin 19, the physical pin number is 35

fans_pwm = None

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Fans
    GPIO.setup(fans_pwm_gpio_pin_num, GPIO.OUT)

    # Tec
    GPIO.setup(tec_pwm_gpio_pin_num, GPIO.OUT)
    GPIO.setup(tec_dir_pin, GPIO.OUT)
    GPIO.output(tec_dir_pin, False)

def read_temp_raw(device_file: str):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

def read_temp(device_file: str):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def main():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    setup()

    global fans_pwm
    fans_pwm = GPIO.PWM(fans_pwm_gpio_pin_num, 25000)
    fans_pwm.start(0)

    global tec_pwm
    tec_pwm = GPIO.PWM(tec_pwm_gpio_pin_num, 60)
    tec_pwm.start(0)

    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    while True:
        _, fahrenheit = read_temp(device_file)
        print(f'Current Temp: {str(round(fahrenheit)) + chr(176)}F')
        if(fahrenheit > 85):
            print("Disabling fans")
            fans_pwm.ChangeDutyCycle(0)
            tec_pwm.ChangeDutyCycle(0)
        else:
            print("Enabling fans")
            fans_pwm.ChangeDutyCycle(100)
            tec_pwm.ChangeDutyCycle(100)

        time.sleep(10)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        fans_pwm.ChangeDutyCycle(0)
        fans_pwm.stop()
        tec_pwm.ChangeDutyCycle(0)
        tec_pwm.stop()
        GPIO.cleanup()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

