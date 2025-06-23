from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


i2c = I2C(0, scl=Pin(19), sda=Pin(18))  # For ESP32


oled = SSD1306_I2C(128, 64, i2c)

oled.fill(0)
oled.text("Hello, Kunal!", 0, 0)
oled.text("Smart Water Heater", 0, 10)
oled.show()
