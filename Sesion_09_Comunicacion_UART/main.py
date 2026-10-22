from machine import UART, Pin, Timer
import time

#  UART0 (8N1)
uart = UART(0, baudrate=9600, bits=8, parity=None, stop=1,
            tx=Pin(0), rx=Pin(1), timeout=100)

#  Salidas
LEDS = {
    "LED1": Pin(13, Pin.OUT),
    "LED2": Pin(14, Pin.OUT),
}
for _led in LEDS.values():
    _led.value(0)

blink_timers = {}   # device -> Timer activo (parpadeo no bloqueante)

BLINK_MIN_MS = 50
BLINK_MAX_MS = 5000


# Control de LEDs
def stop_blink(device):
    """Detiene el parpadeo de un LED si estaba activo."""
    timer = blink_timers.pop(device, None)
    if timer is not None:
        timer.deinit()


def start_blink(device, period_ms):
    """Parpadeo con Timer: no bloquea input() ni el parser."""
    stop_blink(device)
    led = LEDS[device]
    timer = Timer(-1)
    timer.init(period=period_ms, mode=Timer.PERIODIC,
               callback=lambda t: led.value(not led.value()))
    blink_timers[device] = timer


def status_frame():
    """Ejemplo: STATUS,LED1,1,LED2,0"""
    return "STATUS,LED1,{},LED2,{}".format(LEDS["LED1"].value(),
                                           LEDS["LED2"].value())


def set_output(device, value):
    """Aplica 0/1 a LED1, LED2 o ALL. Devuelve True si se ejecuto."""
    if value not in (0, 1):
        return False
    if device == "ALL":
        for name, led in LEDS.items():
            stop_blink(name)
            led.value(value)
        return True
    if device in LEDS:
        stop_blink(device)
        LEDS[device].value(value)
        return True
    return False


# Parser
HELP_TEXT = ("HELP,PING|SET,<LED1|LED2|ALL>,<0|1>|GET,STATUS"
             "|TOGGLE,<LED1|LED2>|BLINK,<LED1|LED2>,<50-5000|0>|HELP")


def handle_frame(frame):
    """Recibe una trama ya limpia y SIEMPRE devuelve una respuesta."""
    frame = frame.strip().upper()
    if not frame:
        return "ERR,EMPTY_FRAME"

    parts = [p.strip() for p in frame.split(",")]
    cmd = parts[0]

    # PING
    if cmd == "PING":
        if len(parts) == 1:
            return "ACK,PONG"
        return "ERR,BAD_PING_FRAME"

    #  HELP
    if cmd == "HELP":
        if len(parts) == 1:
            return HELP_TEXT
        return "ERR,BAD_HELP_FRAME"

    # GET,STATUS
    if cmd == "GET":
        if len(parts) == 2 and parts[1] == "STATUS":
            return status_frame()
        return "ERR,BAD_GET_FRAME"

    # SET,<LED1|LED2|ALL>,<0|1>
    if cmd == "SET":
        if len(parts) != 3:
            return "ERR,BAD_SET_FRAME"
        _, device, value = parts
        if device not in ("LED1", "LED2", "ALL"):
            return "ERR,BAD_DEVICE"
        if value not in ("0", "1"):
            return "ERR,BAD_VALUE"
        if set_output(device, int(value)):
            return "ACK,{},{}".format(device, value)
        return "ERR,SET_FAILED"

    # TOGGLE,<LED1|LED2>
    if cmd == "TOGGLE":
        if len(parts) != 2:
            return "ERR,BAD_TOGGLE_FRAME"
        device = parts[1]
        if device not in LEDS:
            return "ERR,BAD_DEVICE"
        new_value = 0 if LEDS[device].value() else 1
        set_output(device, new_value)
        return "ACK,{},{}".format(device, new_value)

    # BLINK,<LED1|LED2>,<ms>   (ms = 0 detiene el parpadeo)
    if cmd == "BLINK":
        if len(parts) != 3:
            return "ERR,BAD_BLINK_FRAME"
        _, device, ms_text = parts
        if device not in LEDS:
            return "ERR,BAD_DEVICE"
        if not ms_text.isdigit():
            return "ERR,BAD_VALUE"
        ms = int(ms_text)
        if ms == 0:
            stop_blink(device)
            LEDS[device].value(0)
            return "ACK,BLINK,{},0".format(device)
        if ms < BLINK_MIN_MS or ms > BLINK_MAX_MS:
            return "ERR,BAD_PERIOD"
        start_blink(device, ms)
        return "ACK,BLINK,{},{}".format(device, ms)

    # Cualquier otra cosa (texto libre, comandos desconocidos)
    return "ERR,UNKNOWN_CMD"


# ----------------------------------------------------------- Transporte UART
def uart_roundtrip(text, timeout_ms=300):
    """Envia 'text' por GP0/TX y lo lee de vuelta por GP1/RX (loopback).
    Devuelve el texto recibido (sin \\r\\n) o None si no llego nada."""
    # Limpiar basura previa en el buffer RX
    while uart.any():
        uart.read()

    uart.write(text + "\n")                      # sale por GP0 / TX

    start = time.ticks_ms()
    while not uart.any():                        # esperar datos en GP1 / RX
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            return None
        time.sleep_ms(1)

    data = uart.readline()                       # lee hasta '\n' o timeout
    if data is None:
        return None
    try:
        return data.decode().strip()             # bytes -> texto -> sin '\n'
    except UnicodeError:
        return ""                                # bytes corruptos -> ERR luego


def loopback_selftest():
    """Verifica al arrancar que el jumper GP0->GP1 funciona."""
    probe = "LOOP,0"
    echo = uart_roundtrip(probe)
    if echo == probe:
        print("[OK] Loopback UART0 GP0->GP1 verificado.")
        return True
    print("[!!] Loopback FALLO. Revisa jumper GP0->GP1 y baudrate (9600).")
    print("     Recibido:", echo)
    return False


# Main
def main():
    print("=" * 44)
    print(" UART Command Center - Sesion 09")
    print(" UART0 9600 8N1 | TX=GP0 RX=GP1 | LED1=GP13 LED2=GP14")
    print(" Escribe HELP para ver los comandos. Ctrl+C para salir.")
    print("=" * 44)
    loopback_selftest()

    while True:
        try:
            command = input("CMD> ").strip()     # operador por USB (REPL)
        except KeyboardInterrupt:
            break

        received = uart_roundtrip(command)       # la trama cruza el UART fisico
        print("USB CMD:", command)
        print("UART RX:", received)

        if received is None:
            print("RESP:", "ERR,NO_UART_RX")
        else:
            print("RESP:", handle_frame(received))

    # Salida limpia
    for name in list(blink_timers):
        stop_blink(name)
    for led in LEDS.values():
        led.value(0)
    print("Programa detenido.")


main()