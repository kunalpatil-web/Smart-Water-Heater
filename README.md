Project Overview:

This project is a Smart Water Heater Monitoring and Control System built using an ESP32 microcontroller. It integrates temperature sensors, a pressure sensor, an OLED display, touch sensors, a relay for heater control, and a web interface. The system allows users to monitor and control water heating in real time via Wi-Fi using a mobile/PC web browser. It can also function in Access Point (AP) mode for local control without internet.

⚙️ Components Used

1.ESP32:
A Wi-Fi + Bluetooth-enabled microcontroller.
Acts as the main controller, handling sensor data, relay control, and hosting the web server.

2.DS18B20 (Temperature Sensor):
Digital 1-Wire temperature sensor.
Provides accurate water temperature readings.

3.BMP280 (Temperature & Pressure Sensor):
Measures air temperature and atmospheric pressure.
Helps in safety monitoring and logging environmental conditions.

4.OLED Display (I2C, 128x64)
Displays real-time temperature, setpoint, and system status.
Provides a local interface for users.

5.Touch Sensors (Capacitive Sensor):
Capacitive touch inputs used to increase/decrease set temperature.
Provides a button-free user experience.

6.Relay Module
Controls the water heater ON/OFF based on set temperature.
Ensures safe switching of AC loads.




🛠️ Working Principle

DS18B20 continuously monitors water temperature.

BMP280 monitors surrounding pressure and air temperature (optional logging/safety).

OLED displays real-time sensor data and system status.

User sets the desired temperature using touch sensors or via the web interface.

ESP32 controls the relay:
ON → Heater runs when temperature < setpoint.

OFF → Heater stops when temperature ≥ setpoint.

Web interface allows remote monitoring & control via Wi-Fi/AP mode.




✅ Advantages

1.Low-cost and compact system.

2.Remote monitoring & control over Wi-Fi.

3.User-friendly interface (OLED + Web).

4.Touch-based input, no mechanical switches.

5.Expandable for cloud logging (Blynk, MQTT, Firebase).





⚠️ Disadvantages

1.Relay-based control → mechanical wear over time.

2.Wi-Fi dependency for remote monitoring.

3.Limited security (if not encrypted).

4.Power supply fluctuations may affect ESP32 performance.





📌 Applications

1.Smart home water heater automation.

2.Laboratory temperature-controlled baths.

3.Industrial process heating control (scaled version).

4.Educational IoT and automation projects.

5.Integration with MATLAB/SCADA for advanced analysis.





📂 Future Scope

Add PID control for more stable heating.

Integrate Blynk / MQTT / Firebase for cloud access.

Add mobile notifications (temperature reached, safety alerts).

Energy monitoring with current/voltage sensors.



