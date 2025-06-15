import time
from micropython import const

# Register addresses
BME280_I2CADDR = const(0x76)
BME280_REG_CONTROL_HUM = const(0xF2)
BME280_REG_CONTROL = const(0xF4)
BME280_REG_CONFIG = const(0xF5)
BME280_REG_DATA = const(0xF7)

class BME280:
    def __init__(self, i2c, address=BME280_I2CADDR):
        self.i2c = i2c
        self.address = address
        self.dig_T = []
        self.dig_P = []
        self.dig_H = []
        self.t_fine = 0

        self._read_calibration_data()
        self._write_reg(BME280_REG_CONTROL_HUM, 0x01)  # Humidity oversampling x1
        self._write_reg(BME280_REG_CONTROL, 0x27)      # Temp and Pressure oversampling x1, Mode Normal
        self._write_reg(BME280_REG_CONFIG, 0xA0)       # Standby time 1000ms

    def _read_reg(self, reg, length=1):
        return self.i2c.readfrom_mem(self.address, reg, length)

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    def _read_calibration_data(self):
        calib = self._read_reg(0x88, 24)
        self.dig_T = [
            int.from_bytes(calib[0:2], 'little'),
            int.from_bytes(calib[2:4], 'little', signed=True),
            int.from_bytes(calib[4:6], 'little', signed=True)
        ]
        self.dig_P = [int.from_bytes(calib[6+i:8+i], 'little', signed=True) for i in range(0, 18, 2)]
        calib = self._read_reg(0xA1, 1) + self._read_reg(0xE1, 7)
        self.dig_H = [
            calib[0],
            int.from_bytes(calib[1:3], 'little', signed=True),
            calib[3],
            (calib[4] << 4) | (calib[5] & 0x0F),
            (calib[5] >> 4) | (calib[6] << 4),
            calib[7]
        ]

    def read_raw_data(self):
        data = self._read_reg(BME280_REG_DATA, 8)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (data[6] << 8) | data[7]
        return adc_t, adc_p, adc_h

    def compensate_temperature(self, adc_t):
        var1 = ((((adc_t >> 3) - (self.dig_T[0] << 1))) * self.dig_T[1]) >> 11
        var2 = (((((adc_t >> 4) - self.dig_T[0]) * ((adc_t >> 4) - self.dig_T[0])) >> 12) * self.dig_T[2]) >> 14
        self.t_fine = var1 + var2
        return ((self.t_fine * 5 + 128) >> 8) / 100

    def compensate_pressure(self, adc_p):
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P[5]
        var2 += (var1 * self.dig_P[4]) << 17
        var2 += self.dig_P[3] << 35
        var1 = ((var1 * var1 * self.dig_P[2]) >> 8) + ((var1 * self.dig_P[1]) << 12)
        var1 = (((1 << 47) + var1) * self.dig_P[0]) >> 33

        if var1 == 0:
            return 0
        p = 1048576 - adc_p
        p = ((p << 31) - var2) * 3125 // var1
        var1 = (self.dig_P[8] * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P[7] * p) >> 19
        return ((p + var1 + var2) >> 8) / 100

    def compensate_humidity(self, adc_h):
        v_x1 = self.t_fine - 76800
        v_x1 = (((((adc_h << 14) - (self.dig_H[3] << 20) - (self.dig_H[4] * v_x1)) + 16384) >> 15)
                * (((((((v_x1 * self.dig_H[5]) >> 10) * (((v_x1 * self.dig_H[2]) >> 11) + 32768)) >> 10) + 2097152)
                * self.dig_H[1] + 8192) >> 14))
        v_x1 -= (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * self.dig_H[0]) >> 4)
        v_x1 = max(v_x1, 0)
        v_x1 = min(v_x1, 419430400)
        return (v_x1 >> 12) / 1024

    def read_compensated_data(self):
        adc_t, adc_p, adc_h = self.read_raw_data()
        temp = self.compensate_temperature(adc_t)
        pres = self.compensate_pressure(adc_p)
        hum = self.compensate_humidity(adc_h)
        return temp, pres, hum
