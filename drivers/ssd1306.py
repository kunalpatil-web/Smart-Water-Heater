# MicroPython SSD1306 OLED driver, I2C interface
# Source: https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py

import framebuf

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.poweron()
        self.init_display()

    def init_display(self):
        for cmd in (
            0xae,         # display off
            0x20, 0x00,   # set memory addressing mode to horizontal
            0x40,         # set display start line
            0xa1,         # set segment re-map
            0xc8,         # set COM output scan direction
            0xda, 0x12,   # set COM pins hardware configuration
            0x81, 0xcf,   # set contrast control
            0xa4,         # display all on resume
            0xa6,         # set normal display
            0xd5, 0x80,   # set display clock divide ratio/oscillator frequency
            0x8d, 0x14 if not self.external_vcc else 0x10,  # charge pump setting
            0xaf):        # display on
            self.write_cmd(cmd)

    def poweron(self):
        pass  # no-op for I2C

    def poweroff(self):
        self.write_cmd(0xae)

    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(0xa7 if invert else 0xa6)

    def show(self):
        for page in range(0, self.height // 8):
            self.write_cmd(0xb0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            self.write_data(self.buffer[page * self.width:(page + 1) * self.width])

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def blit(self, fbuf, x, y):
        self.framebuf.blit(fbuf, x, y)

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)
