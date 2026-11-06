# Alumnos: Jonathan Hernández Lazcano, Camila Rodriguez Rosas
# Matriculas: 200417, 194100
# Laboratorio de Elementos Programables - Sesion 10
# Challenge 10: Smart I2C HMI Monitor

from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from time import ticks_ms, ticks_diff, sleep_ms


# ---------------------------------------------------------------
# 1) Bus I2C0 y scan. Direcciones SSD1306 comunes: 0x3C y 0x3D.
# ---------------------------------------------------------------
I2C_ID = 0
SDA_PIN = 4
SCL_PIN = 5
I2C_FREQ = 400_000
OLED_WIDTH = 128
OLED_HEIGHT = 64

i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
devices = i2c.scan()

# Evidencia del scan (decimal y hexadecimal) para scan.png y README.
print("Decimal:", devices)
print("Hex:", [hex(a) for a in devices])

oled = None
oled_address = None

for address in (0x3C, 0x3D):
    if address in devices:
        try:
            oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=address)
            oled_address = address
            break
        except Exception as error:
            print("No se pudo iniciar OLED en", hex(address), error)

if oled is None:
    print("OLED no detectado. Revisa SDA=GP4, SCL=GP5, VCC=3V3 y GND.")
else:
    print("OLED detectado en", hex(oled_address))


# ---------------------------------------------------------------
# 2) Entradas y salidas
# ---------------------------------------------------------------
adc = ADC(26)                          # Potenciometro en GP26 (ADC0)
button = Pin(16, Pin.IN, Pin.PULL_UP)  # Boton a GND -> presionado = 0
led_alarm = Pin(15, Pin.OUT)           # LED de alarma

page = 0
last_button = button.value()
last_change_ms = 0
last_refresh_ms = 0
debounce_ms = 35
refresh_ms = 100

samples = 0
min_value = 100.0
max_value = 0.0


# ---------------------------------------------------------------
# 3) Logica de estados
# ---------------------------------------------------------------
def classify(percent):
    """Umbrales: NORMAL <50%, WARNING <75%, ALARM >=75%."""
    if percent < 50:
        return "NORMAL"
    if percent < 75:
        return "WARNING"
    return "ALARM"


# ---------------------------------------------------------------
# 4) Pantallas de la HMI
# ---------------------------------------------------------------
def draw_bar(percent):
    oled.rect(3, 48, 122, 12, 1)
    bar_width = int(118 * percent / 100)
    if bar_width > 0:
        oled.fill_rect(5, 51, bar_width, 6, 1)


def live_screen(percent, state):
    oled.text("PAGE 1 - LIVE", 0, 0)
    oled.text("ADC: {:5.1f}%".format(percent), 0, 16)
    oled.text("Estado: " + state, 0, 28)
    draw_bar(percent)


def bus_screen():
    oled.text("PAGE 2 - I2C", 0, 0)
    oled.text("SDA:GP{} SCL:GP{}".format(SDA_PIN, SCL_PIN), 0, 14)
    oled.text("Freq: {} kHz".format(I2C_FREQ // 1000), 0, 26)
    oled.text("OLED: {}".format(hex(oled_address)), 0, 38)
    oled.text("Dev: " + " ".join(hex(a) for a in devices), 0, 50)


def stats_screen():
    oled.text("PAGE 3 - STATS", 0, 0)
    oled.text("Min: {:5.1f}%".format(min_value), 0, 17)
    oled.text("Max: {:5.1f}%".format(max_value), 0, 30)
    oled.text("Muestras: {}".format(samples), 0, 43)


# ---------------------------------------------------------------
# 5) Bucle principal (sin sleeps largos)
# ---------------------------------------------------------------
while True:
    now = ticks_ms()

    # Muestreo continuo y estadisticas.
    raw = adc.read_u16()
    percent = raw * 100.0 / 65535
    state = classify(percent)
    samples += 1
    min_value = min(min_value, percent)
    max_value = max(max_value, percent)

    # LED ALARM.
    led_alarm.value(1 if state == "ALARM" else 0)

    # Boton por flanco 1 -> 0 con antirrebote.
    # Cualquier cambio (presionar o soltar) reinicia la ventana,
    # asi el rebote al soltar no cuenta como otra pulsacion.
    current_button = button.value()
    if (current_button != last_button
            and ticks_diff(now, last_change_ms) >= debounce_ms):
        if current_button == 0:
            page = (page + 1) % 3
            print("Cambio a pagina", page + 1)
        last_change_ms = now
    last_button = current_button

    # Refresco de pantalla: fill -> draw -> show.
    if oled is not None and ticks_diff(now, last_refresh_ms) >= refresh_ms:
        try:
            oled.fill(0)
            if page == 0:
                live_screen(percent, state)
            elif page == 1:
                bus_screen()
            else:
                stats_screen()
            oled.show()
        except Exception as error:
            # Si se desconecta el display, el muestreo sigue corriendo.
            print("Error al actualizar OLED:", error)
            oled = None
        last_refresh_ms = now

    sleep_ms(20)