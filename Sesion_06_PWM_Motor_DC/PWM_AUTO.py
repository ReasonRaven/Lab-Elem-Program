# MODO = "AUTO"   -> secuencia del CHALLENGE 06 (reto base)
# MODO = "MANUAL" -> botones + potenciometro (bonus)
# =====================================================================

from machine import Pin, PWM, ADC
from time import sleep_ms, ticks_ms, ticks_diff

MODO = "AUTO"          # cambia a "MANUAL" para el bonus

# ---------------- Configuracion de hardware ----------------
IN1 = Pin(2, Pin.OUT)
IN2 = Pin(3, Pin.OUT)
ENA = PWM(Pin(4))
ENA.freq(1000)

btn_fwd = Pin(14, Pin.IN, Pin.PULL_UP)
btn_rev = Pin(15, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(16, Pin.IN, Pin.PULL_UP)
pot = ADC(26)

# ---------------- Funciones basicas ----------------
def set_speed(percent):
    # Acelerador: limita a 0..100 % y lo convierte a duty de 16 bits
    percent = max(0, min(100, percent))
    duty = int(percent * 65535 / 100)
    ENA.duty_u16(duty)


def forward():
    IN1.value(1)
    IN2.value(0)


def reverse():
    IN1.value(0)
    IN2.value(1)


def stop():
    set_speed(0)
    IN1.value(0)
    IN2.value(0)


def ramp_to(start, end, step=10, delay_ms=100):
    # Cambia la velocidad poco a poco de start a end (sube o baja)
    start = max(0, min(100, start))
    end = max(0, min(100, end))

    if start <= end:
        secuencia = range(start, end + 1, step)      # subir: paso positivo
        etiqueta = "Acelerando"
    else:
        secuencia = range(start, end - 1, -step)     # bajar: paso negativo
        etiqueta = "Desacelerando"

    speed = start
    for speed in secuencia:
        set_speed(speed)
        print(etiqueta, speed, "%")
        sleep_ms(delay_ms)

    # Si el paso no cae exacto (ej. 0 -> 75 con paso 10), asegura el valor final
    if speed != end:
        set_speed(end)
        print(etiqueta, end, "%")
        sleep_ms(delay_ms)


def change_direction(new_dir, current_speed):
    # Regla de seguridad: nunca invertir sin pasar por 0 %
    print("Cambio seguro de direccion: bajando a 0 % primero")
    ramp_to(current_speed, 0)
    stop()
    sleep_ms(300)
    new_dir()


def speed_test():
    # Prueba para la tabla: 25 / 50 / 75 / 100 %
    print("=== PRUEBA DE VELOCIDADES ===")
    forward()
    for p in [25, 50, 75, 100]:
        set_speed(p)
        print("Prueba velocidad:", p, "%")
        sleep_ms(1500)
    ramp_to(100, 0)
    stop()
    print("MOTOR STOP")


# ---------------- MODO AUTO: reto base ----------------
def modo_auto():
    stop()
    print("MOTOR STOP")
    sleep_ms(1000)

    speed_test()
    sleep_ms(1000)

    while True:
        print("=== FORWARD ===")
        forward()
        ramp_to(0, 100)
        print("Mantener 100 %")
        sleep_ms(2000)

        change_direction(reverse, 100)
        print("=== REVERSE ===")
        ramp_to(0, 75)
        print("Mantener 75 %")
        sleep_ms(2000)

        ramp_to(75, 0)
        stop()
        print("MOTOR STOP")
        sleep_ms(2000)


# ---------------- MODO MANUAL: bonus ----------------
# Las ISR solo guardan la peticion (regla de oro de la Sesion 04)
pedido = 0          # 1 = forward, -1 = reverse, 0 = stop
ultimo_click = 0


def boton_irq(pin):
    global pedido, ultimo_click
    ahora = ticks_ms()
    if ticks_diff(ahora, ultimo_click) < 150:     # debounce
        return
    ultimo_click = ahora
    if pin is btn_fwd:
        pedido = 1
    elif pin is btn_rev:
        pedido = -1
    else:
        pedido = 0


def leer_pot_percent():
    # ADC de 16 bits (0..65535) -> 0..100 %
    return int(pot.read_u16() * 100 / 65535)


def modo_manual():
    btn_fwd.irq(trigger=Pin.IRQ_FALLING, handler=boton_irq)
    btn_rev.irq(trigger=Pin.IRQ_FALLING, handler=boton_irq)
    btn_stop.irq(trigger=Pin.IRQ_FALLING, handler=boton_irq)

    direccion = 0       # direccion real actual del motor
    velocidad = 0       # velocidad real actual
    PASO = 2            # % por ciclo -> rampa suave
    ultimo_print = ""

    stop()
    print("MODO MANUAL: F = forward, R = reverse, S = stop, pot = velocidad")

    while True:
        # 1) Decidir la velocidad objetivo
        if pedido != direccion:
            objetivo = 0                    # hay que frenar antes de cambiar
        elif direccion == 0:
            objetivo = 0
        else:
            objetivo = leer_pot_percent()

        # 2) Rampa: acercarse al objetivo poco a poco (sin bloquear)
        if velocidad < objetivo:
            velocidad = min(velocidad + PASO, objetivo)
        elif velocidad > objetivo:
            velocidad = max(velocidad - PASO, objetivo)
        set_speed(velocidad)

        # 3) Solo cambiar direccion cuando ya estamos en 0 %
        if velocidad == 0 and pedido != direccion:
            direccion = pedido
            if direccion == 1:
                forward()
            elif direccion == -1:
                reverse()
            else:
                stop()

        # 4) Imprimir solo cuando cambia algo
        nombre = {1: "FORWARD", -1: "REVERSE", 0: "STOP"}[direccion]
        estado = nombre + " " + str(velocidad) + " %"
        if estado != ultimo_print:
            print(estado)
            ultimo_print = estado

        sleep_ms(40)


# ---------------- Arranque ----------------
if MODO == "MANUAL":
    modo_manual()
else:
    modo_auto()