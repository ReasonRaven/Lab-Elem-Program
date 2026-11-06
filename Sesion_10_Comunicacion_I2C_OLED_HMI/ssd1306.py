# ssd1306.py
# Driver didactico compacto para OLED SSD1306 128x64 por I2C.
# Compatible con MicroPython + framebuf. Pensado para esta practica.

from micropython import const
import framebuf

_SET_CONTRAST = const(0x81)
_SET_ENTIRE_ON = const(0xA4)
_SET_NORM_INV = const(0xA6)
_SET_DISP = const(0xAE)
_SET_MEM_ADDR = const(0x20)
_SET_COL_ADDR = const(0x21)
_SET_PAGE_ADDR = const(0x22)
_SET_DISP_START_LINE = const(0x40)
_SET_SEG_REMAP = const(0xA0)
_SET_MUX_RATIO = const(0xA8)
_SET_COM_OUT_DIR = const(0xC0)
_SET_DISP_OFFSET = const(0xD3)
_SET_COM_PIN_CFG = const(0xDA)
_SET_DISP_CLK_DIV = const(0xD5)
_SET_PRECHARGE = const(0xD9)
_SET_VCOM_DESEL = const(0xDB)
_SET_CHARGE_PUMP = const(0x8D)


class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        if width != 128 or height != 64:
            raise ValueError('Este driver didactico espera OLED 128x64')
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = height // 8
        self.buffer = bytearray(width * self.pages)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer, width, height, framebuf.MONO_VLSB
        )
        self._init_display()

    def _cmd(self, value):
        self.i2c.writeto(self.addr, bytes((0x00, value)))

    def _init_display(self):
        sequence = (
            _SET_DISP | 0x00,
            _SET_MEM_ADDR, 0x00,
            _SET_DISP_START_LINE,
            _SET_SEG_REMAP | 0x01,
            _SET_MUX_RATIO, 0x3F,
            _SET_COM_OUT_DIR | 0x08,
            _SET_DISP_OFFSET, 0x00,
            _SET_COM_PIN_CFG, 0x12,
            _SET_DISP_CLK_DIV, 0x80,
            _SET_PRECHARGE, 0xF1,
            _SET_VCOM_DESEL, 0x30,
            _SET_CONTRAST, 0xFF,
            _SET_ENTIRE_ON,
            _SET_NORM_INV,
            _SET_CHARGE_PUMP, 0x14,
            _SET_DISP | 0x01,
        )
        for value in sequence:
            self._cmd(value)
        self.fill(0)
        self.show()

    def show(self):
        self._cmd(_SET_COL_ADDR)
        self._cmd(0)
        self._cmd(self.width - 1)
        self._cmd(_SET_PAGE_ADDR)
        self._cmd(0)
        self._cmd(self.pages - 1)
        # 0x40 indica datos de display en SSD1306.
        self.i2c.writeto(self.addr, b'\x40' + self.buffer)

    def poweroff(self): self._cmd(_SET_DISP | 0x00)
    def poweron(self): self._cmd(_SET_DISP | 0x01)
    def contrast(self, value):
        self._cmd(_SET_CONTRAST); self._cmd(value & 0xFF)
    def invert(self, value): self._cmd(_SET_NORM_INV | (value & 1))

    # Primitivas delegadas a framebuf
    def fill(self, c): return self.framebuf.fill(c)
    def pixel(self, x, y, c=1): return self.framebuf.pixel(x, y, c)
    def text(self, s, x, y, c=1): return self.framebuf.text(s, x, y, c)
    def line(self, x1, y1, x2, y2, c=1): return self.framebuf.line(x1, y1, x2, y2, c)
    def hline(self, x, y, w, c=1): return self.framebuf.hline(x, y, w, c)
    def vline(self, x, y, h, c=1): return self.framebuf.vline(x, y, h, c)
    def rect(self, x, y, w, h, c=1): return self.framebuf.rect(x, y, w, h, c)
    def fill_rect(self, x, y, w, h, c=1): return self.framebuf.fill_rect(x, y, w, h, c)
