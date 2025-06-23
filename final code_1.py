import usocket as socket
import network
from machine import Pin, SoftI2C, I2C
import machine
from time import sleep
import ujson
import _thread
import onewire
import ds18x20
import ssd1306
from bmp280 import BMP280

# Wi-Fi Access Point Setup 
ssid = "KUNAL_ESP"
password = "kunal007"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

while not ap.active():
    pass

ip = ap.ifconfig()[0]
print("Access Point active. Connect to Wi-Fi:")
print("SSID:", ssid)
print("Access at: http://{}/".format(ip))

# Sensor & Display Initialization 

# BMP280 
i2c_bmp = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
bmp = BMP280(i2c_bmp, addr=0x76)

# DS18B20 
#connect signal wire to GPIO4
ds_pin = Pin(4)
ow = onewire.OneWire(ds_pin)
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
print("Found DS18B20 devices:", roms)

# OLED 
i2c_oled = SoftI2C(scl=Pin(19), sda=Pin(18))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# OLED Starting Message
oled.fill(0)
oled.text("SMART WATER", 20, 0)
oled.text("HEATER", 40, 10)
oled.text("BY: KUNAL PATIL", 0, 30)
oled.text("    TANUJA PATIL", 0, 45)
oled.show()
sleep(3)
oled.fill(0)
oled.show()

# Touch sensors 
touch_increase = Pin(33, Pin.IN) #For Increase
touch_decrease = Pin(25, Pin.IN) # for Decrease

# Relay
relay = Pin(13, Pin.OUT)

# Initial parameters
set_temp = 25
humidity = 40.0  


def read_bmp280():
    try:
        temperature, pressure = bmp.read_compensated_data()
        return round(temperature, 2), round(pressure / 100.0, 2)
    except Exception as e:
        print("BMP280 Error:", e)
        return None, None


def load_html(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except:
        return "<h1>404 - File Not Found</h1>"

def handle_web_request(conn, request):
    global set_temp
    if 'POST /set_temp' in request:
        try:
            payload = request.split('\r\n\r\n', 1)[1]
            data = ujson.loads(payload)
            set_temp = float(data.get('set_temp', set_temp))
            print("Set temperature updated to:", set_temp)
            response = ujson.dumps({'success': True})
        except:
            response = ujson.dumps({'success': False})
        conn.send('HTTP/1.1 200 OK\nContent-Type: application/json\n\n')
        conn.sendall(response.encode())

    elif 'GET /data' in request:
        temp_bmp, pressure = read_bmp280()
        if temp_bmp is not None:
            response = ujson.dumps({'temp': temp_bmp, 'pressure': pressure, 'humidity': humidity})
        else:
            response = ujson.dumps({'temp': 'N/A', 'pressure': 'N/A', 'humidity': 'N/A'})
        conn.send('HTTP/1.1 200 OK\nContent-Type: application/json\n\n')
        conn.sendall(response.encode())

    elif 'GET /Next.html' in request:
        response = load_html('Next.html')
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        conn.sendall(response)

    else:
        response = load_html('index.html')
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        conn.sendall(response)

    conn.close()

def web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("Web server started at http://{}".format(ip))
    while True:
        conn, addr = s.accept()
        print("Request from:", addr)
        request = conn.recv(1024).decode()
        handle_web_request(conn, request)

# Control Logic
def control_loop():
    global set_temp
    if not roms:
        print("No DS18B20 sensor found.")
        return

    while True:
        ds.convert_temp()
        sleep(0.75)

        for rom in roms:
            temp_ds = ds.read_temp(rom)
            temp_bmp, pressure = read_bmp280()

            # Touch inputs
            if touch_increase.value():
                set_temp = min(set_temp + 1, 100)
                print("[Touch] Increase button pressed. Set Temp:", set_temp)
                sleep(0.2)

            if touch_decrease.value():
                set_temp = max(set_temp - 1, 1)
                print("[Touch] Decrease button pressed. Set Temp:", set_temp)
                sleep(0.2)

            # Heater control logic
            if temp_ds < set_temp - 1:
                relay.value(1)
                relay_status = "ON"
            elif temp_ds > set_temp + 1:
                relay.value(0)
                relay_status = "OFF"
            else:
                relay_status = "IDLE"

            # OLED Display Output
            oled.fill(0)
            oled.text("C.Temp: {:.1f} C".format(temp_ds), 0, 0)
            if pressure is not None:
                oled.text("Press: {:.1f} hPa".format(pressure), 0, 16)
            else:
                oled.text("BMP280 Err", 0, 16)
            oled.text("Set Temp: {:.1f}".format(set_temp), 0, 32)
            oled.text("Heater: {}".format(relay_status), 0, 48)
            oled.show()

            # For Thonny Terminal 
            print("\n===== STATUS =====")
            print("Current Temp   : {:.2f} °C".format(temp_ds))
            if pressure is not None:
                print("BMP280 Pressure: {:.2f} hPa".format(pressure))
            else:
                print("BMP280 Error")
            print("Set Temp       : {:.2f} °C".format(set_temp))
            print("Heater Status  : {}".format(relay_status))
            print("==================")

            sleep(0.5)


def main():
    _thread.start_new_thread(web_server, ())
    control_loop()

main()
