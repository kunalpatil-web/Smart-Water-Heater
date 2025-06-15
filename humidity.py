from machine import I2C, Pin
from bmp280 import BMP280
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # Adjust pins as per your wiring
bmp = BMP280(i2c)

while True:
    temperature, pressure = bmp.read_compensated_data()
    print("Temperature:", temperature, "°C")
    print("Pressure:", pressure, "hPa")
    time.sleep(2)
