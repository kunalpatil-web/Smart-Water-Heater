import usocket as socket
import network
from machine import Pin, I2C
import esp
from time import sleep
import bmp280
import ujson


# Wi-Fi configuration
ssid = "KUNAL"
password = 'kunal007'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

while not ap.active():
    pass

print('Connection successful')
print(ap.ifconfig())


