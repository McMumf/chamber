import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 24 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 26 to be an input pin and set initial value to be pulled low (off)

def main():

    while True: # Run forever
        if GPIO.input(38) == GPIO.HIGH:
            print("Blue Button was pushed!")
        if GPIO.input(40) == GPIO.HIGH:
            print("Red Button was pushed!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            print(e)
        GPIO.cleanup()
