from machine import Pin
from time import sleep

# Connect relay IN pin or LED to GPIO 26 (you can change it)
relay = Pin(13, Pin.OUT)

while True:
    relay.value(1)  # Turn ON relay or LED
    print("Relay ON")
    sleep(5)        # Wait for 5 seconds

    relay.value(0)  # Turn OFF relay or LED
    print("Relay OFF")
    sleep(3)        # Wait for 3 seconds
