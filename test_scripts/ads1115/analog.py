import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import math

# Initialize the I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)

# Define the analog input channel
channel = AnalogIn(ads, ADS.P0)

R_25 = 2252 # Resistance at 25 deg C
V_REF = 3.3 # Resistance of voltage divider resistor
R_f = 1100  # Resistance of voltage divider resistor
T_K_0 = 273.15 # Temp in Kelvin at 0 Deg C

A = float("3.3540154E-03")
B = float("2.5627725E-04")
C = float("2.0829210E-06")
D = float("7.3003206E-08")

# Loop to read the analog input continuously
while True:
    print("Analog Value: ", channel.value, "\nVoltage: ", channel.voltage)
    v_t = channel.voltage * V_REF / 1023 # Input Voltage at Temp
    r_t = R_f * v_t / (V_REF - v_t) # Thermistor resistance at temp
    r_norm = math.log(r_t/R_25)

    temp_K = 1 / (A + (B * r_norm) + (C * pow(r_norm, 2)) + (D * pow(r_norm, 3)))
    
    temp = temp_K - T_K_0

    print("Temp in C: ", temp)

    time.sleep(0.2)
