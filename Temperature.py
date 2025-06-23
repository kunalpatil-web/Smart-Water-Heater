import machine
import onewire
import ds18x20
import time


ds_pin = machine.Pin(4)


ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))


roms = ds_sensor.scan()
print('Found DS18B20 devices:', roms)


while True:
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)  
        for rom in roms:
            temp = ds_sensor.read_temp(rom)
            print("Temperature: {:.2f} °C".format(temp))
        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)
