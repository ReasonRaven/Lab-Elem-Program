from machine import UART, Pin
from time import sleep_ms, ticks_ms, ticks_diff

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
led1 = Pin(13, Pin.OUT)
led2 = Pin(14, Pin.OUT)

def clear_rx():
    while uart.any():
        uart.read()

def receive_complete_line(timeout_ms=1000):

    buffer = bytearray()
    start = ticks_ms()

    while ticks_diff(ticks_ms(), start) < timeout_ms:
        while uart.any():
            byte = uart.read(1)

            if not byte:
                break

            if byte == b"\n":
                return buffer.decode().rstrip("\r")

            buffer.extend(byte)

        sleep_ms(1)
    
    return None
def  uart_roundtrip(text, timeout_ms=1000):
    clear_rx()

    uart.write((text + "\n").encode())

    return receive_complete_line(timeout_ms)

def status_frame():
    return "STATUS, LED1,{}, LED2,{}".format(led1.value(), led2.value())

def set_output(device, value):
    if value not in ("0", "1"):
        return False

    output_value = int(value)

    if device == "LED1":
        led1.value(output_value)
        return True

    if device == "LED2":
        led2.value(output_value)
        return True

    if device == "ALL":
        led1.value(output_value)
        led2.value(output_value)
        return True

    return False

def handle_frame(frame):
    frame = frame.upper()
    if frame == "PING":
        return "ACK, PONG"

    if frame == "GET, STATUS":
        return status_frame()

    parts = frame.split(",")

    if len(parts) == 3 and parts[0] == "SET":
        _, device, value = parts

        if set_output(device, value):
            return "ACK, {}, {}".format(device, value)

        return "ERR, BAD_SET_FRAME"

    return "ERR,UNKONWN_FRAME"

print("AEGURATE QUE EL JUMPER ESTE CONECTADO")
print("COMANDOS: PING | SET,LED1,1 | SET,LED2,1 | GET,STATUS")

while True:

    try:
        command = input("CMD> ".strip())
    except KeyboardInterrupt:
        print("Programa Detenido")
        break

    if not command:
        continue

    print("USB CMD:", command)
    received = uart_roundtrip(command)

    if received is None:
        print("UART RX : SIN DATOS. Checar Conexcion")
        continue

    print("UART RX : ", received)
    print("RESP    :",handle_frame(received))
