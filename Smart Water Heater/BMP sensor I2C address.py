from machine import Pin, I2C
import time

# Initialize I2C on GPIO21 (SDA) and GPIO22 (SCL)
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)

# Scan for devices
print("Scanning I2C bus...")
devices = i2c.scan()

if devices:
    print("I2C devices found:", len(devices))
    for device in devices:
        print("Decimal address:", device, " | Hex address: 0x{:02X}".format(device))
else:
    print("No I2C devices found.")
