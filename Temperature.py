import machine
import onewire
import ds18x20
import time

# Connect DS18B20 data line to GPIO 13 (you can change this)
ds_pin = machine.Pin(4)

# Setup 1-Wire and DS18B20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# Scan for sensors on the 1-Wire bus
roms = ds_sensor.scan()
print('Found DS18B20 devices:', roms)

# Main loop to read and print temperature
while True:
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)  # Wait for conversion
        for rom in roms:
            temp = ds_sensor.read_temp(rom)
            print("Temperature: {:.2f} °C".format(temp))
        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)
