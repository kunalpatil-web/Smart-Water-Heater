import time
import struct

class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr
        self._load_calibration()
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')  # Normal mode, temp and pressure oversampling x1
        self.i2c.writeto_mem(self.addr, 0xF5, b'\xA0')  # Config

    def _load_calibration(self):
        # Read 24 bytes of calibration data from 0x88
        calib = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        self.dig_T1, self.dig_T2, self.dig_T3 = struct.unpack('<Hhh', calib[0:6])
        self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, self.dig_P6, \
        self.dig_P7, self.dig_P8, self.dig_P9 = struct.unpack('<Hhhhhhhhh', calib[6:24])

    def read_raw_data(self):
        # Read raw pressure and temperature data
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return adc_t, adc_p

    def compensate_temperature(self, adc_t):
        var1 = (((adc_t >> 3) - (self.dig_T1 << 1)) * self.dig_T2) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T1) * ((adc_t >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        self.t_fine = var1 + var2
        temp = (self.t_fine * 5 + 128) >> 8
        return temp / 100  # °C

    def compensate_pressure(self, adc_p):
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0  # avoid exception caused by division by zero
        p = 1048576 - adc_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        pressure = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        return pressure / 25600  # hPa

    def read_compensated_data(self):
        adc_t, adc_p = self.read_raw_data()
        temp = self.compensate_temperature(adc_t)
        pressure = self.compensate_pressure(adc_p)
        return temp, pressure
