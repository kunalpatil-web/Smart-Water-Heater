from machine import Pin, PWM, SoftI2C
import onewire, ds18x20, ssd1306, time

# --- DS18B20 Temperature Sensor Setup ---
ds_pin = Pin(4)  # GPIO4
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

def read_temp():
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    return ds_sensor.read_temp(roms[0])

# --- PID Controller Class ---
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.integral = 0
        self.prev_error = 0

    def compute(self, input_val):
        error = self.setpoint - input_val
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        return max(0, min(1023, output))  # Clamp to 0–1023

# --- OLED Setup (SoftI2C) ---
i2c = SoftI2C(scl=Pin(19), sda=Pin(18))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# --- PWM Output Setup (GPIO15) ---
pwm = PWM(Pin(15), freq=1000)

# --- PID Initialization ---
pid = PID(Kp=25.0, Ki=0.5, Kd=5.0, setpoint=35)  # Target temp: 40°C

# --- Main Loop ---
while True:
    temp = read_temp()
    output = pid.compute(temp)
    pwm.duty(int(output))  # Send PWM signal to GPIO15

    # Calculate PWM in %
    pwm_percent = (output / 1023) * 100

    # Display on OLED
    oled.fill(0)
    oled.text("Temp: {:.1f} C".format(temp), 0, 0)
    oled.text("Set : {:.1f} C".format(pid.setpoint), 0, 12)
    oled.text("PWM:{:.0f} ({:.1f}%)".format(output, pwm_percent), 0, 24)
    oled.show()

    # Print to serial
    print("Temp: {:.1f} C | Setpoint: {:.1f} C | PWM: {:.0f} ({:.1f}%)".format(
        temp, pid.setpoint, output, pwm_percent))

    time.sleep(1)
