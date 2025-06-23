from machine import Pin
from time import sleep


relay = Pin(13, Pin.OUT)

while True:
    relay.value(1) 
    print("Relay ON")
    sleep(5)        

    relay.value(0) 
    print("Relay OFF")
    sleep(3)        
