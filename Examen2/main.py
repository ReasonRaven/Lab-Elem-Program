from machine import Pin, PWM, ADC
import _thread
import time

PIN_LED_DIG = 13
PIN_LED_PWM = 15
PIN_BOTON   = 16
PIN_ADC     = 26

PWM_FREQ    = 1000      # 1 kHz para no ver parpadeo
ADC_PERIODO = 0.05      # Core 1 mide cada 50 ms, aprox 20 muestras por segundo
ADC_PROMEDIO = 8        # Suavizar ruido
DEBOUNCE_MS = 50        # Antirrebote 

led_dig = Pin(PIN_LED_DIG, Pin.OUT)
led_pwm = PWM(Pin(PIN_LED_PWM))
led_pwm.freq(PWM_FREQ)
boton   = Pin(PIN_BOTON, Pin.IN, Pin.PULL_UP)
adc     = ADC(PIN_ADC)

estado = {
    "led": 0,          # 0/1 LED digital
    "pwm": 0,          # 0..100 %
    "adc_raw": 0,      # 0..65535
    "adc_pct": 0,      # 0..100 %
    "btn": 0,          # 1 = presionado, 0 = suelto
    "samples": 0,      # muestras tomadas por Core 1
}

lock       = _thread.allocate_lock()
print_lock = _thread.allocate_lock()   # evita que los dos núcleos impriman encimado
corriendo  = True                      # bandera para detener Core 1 


def imprimir(texto):
    """Imprime sin que Core 0 y Core 1 mezclen sus líneas."""
    with print_lock:
        print(texto)


def pct_a_duty(pct):
    """Convierte 0-100 % al rango de duty_u16 (0-65535)"""
    return pct * 65535 // 100


def set_led(valor):
    led_dig.value(valor)
    with lock:
        estado["led"] = valor


def set_pwm(pct):
    led_pwm.duty_u16(pct_a_duty(pct))
    with lock:
        estado["pwm"] = pct


def texto_status():
    with lock:
        s = dict(estado)

    # Formato exacto del examen + RAW como campo extra al final
    return "STATUS,LED={},PWM={},ADC={},BTN={},SAMPLES={},RAW={}".format(
        s["led"],
        s["pwm"],
        s["adc_pct"],
        s["btn"],
        s["samples"],
        s["adc_raw"]
    )


def leer_adc_promedio():
    total = 0

    for _ in range(ADC_PROMEDIO):
        total += adc.read_u16()
        time.sleep_us(500)

    return total // ADC_PROMEDIO


def tarea_core1():
    ahora = time.ticks_ms()

    # Estado inicial real del boton
    btn_inicial = 1 if boton.value() == 0 else 0
    btn_estable = btn_inicial
    btn_candidato = btn_inicial
    tiempo_candidato = ahora

    # BTN en STATUS funciona como interruptor con memoria (latch):
    # cada presion cambia 0 -> 1 o 1 -> 0 y se queda asi al soltar
    with lock:
        estado["btn"] = 0

    while corriendo:
        # ADC
        raw = leer_adc_promedio()
        pct = raw * 100 // 65535

        # Lectura instantanea del boton
        btn_lectura = 1 if boton.value() == 0 else 0
        ahora = time.ticks_ms()

        # Detectar un posible cambio
        if btn_lectura != btn_candidato:
            btn_candidato = btn_lectura
            tiempo_candidato = ahora

        # Validar que el cambio permanezca estable
        if (
            btn_candidato != btn_estable
            and time.ticks_diff(
                ahora, tiempo_candidato
            ) >= DEBOUNCE_MS
        ):
            btn_estable = btn_candidato

            # Evento solamente al presionar (no al soltar)
            if btn_estable == 1:
                with lock:
                    estado["btn"] = 0 if estado["btn"] else 1
                imprimir("EVENT,BTN_PRESSED")
                imprimir(texto_status())

        # Actualizar mediciones
        with lock:
            estado["adc_raw"] = raw
            estado["adc_pct"] = pct
            estado["samples"] += 1

        time.sleep(ADC_PERIODO)


def validar_bin(partes):
    """Valida comandos tipo X,0 / X,1. Regresa (valor, error)."""
    if len(partes) != 2 or partes[1] == "":
        return None, "ERR,BAD_FORMAT"
    if partes[1] not in ("0", "1"):
        return None, "ERR,BAD_VALUE"
    return int(partes[1]), None


def procesar(linea):
    """Recibe una línea de texto y regresa la respuesta."""
    linea = linea.strip().upper()
    if not linea:
        return None                          # línea vacía: se ignora

    partes = [p.strip() for p in linea.split(",")]
    cmd = partes[0]

    # PING
    if cmd == "PING":
        if len(partes) != 1:
            return "ERR,BAD_FORMAT"
        return "PONG"

    # LED,0 | LED,1
    if cmd == "LED":
        valor, err = validar_bin(partes)
        if err:
            return err
        set_led(valor)
        return "ACK,LED,{}".format(valor)

    # PWM,n
    if cmd == "PWM":
        if len(partes) != 2 or partes[1] == "":
            return "ERR,BAD_FORMAT"
        try:
            n = int(partes[1])
        except ValueError:
            return "ERR,BAD_VALUE"
        if n < 0 or n > 100:
            return "ERR,PWM_RANGE"
        set_pwm(n)
        return "ACK,PWM,{}".format(n)

    # STATUS
    if cmd == "STATUS":
        if len(partes) != 1:
            return "ERR,BAD_FORMAT"
        return texto_status()

    # ALL,0 / ALL,1 
    if cmd == "ALL":
        valor, err = validar_bin(partes)
        if err:
            return err
        set_led(valor)
        set_pwm(100 if valor == 1 else 0)
        return "ACK,ALL,{}".format(valor)

    #BONUS HELP
    if cmd == "HELP":
        return "\n".join([
            "===================== HELP =====================",
            "LED 1 = LED rojo -> solo encendido/apagado",
            "LED 2 = LED naranja -> brillo por PWM 0-100 %",
            "------------------------------------------------",
            "comandos: ",
            "PING        -> PONG",
            "LED,1       Enciende LED 1 (rojo)",
            "LED,0       Apaga LED 1 (rojo)",
            "PWM,n       Brillo de LED 2 (naranja), n = 0..100",
            "            Ej: PWM,0 apaga, PWM,50 medio, PWM,100 maximo",
            "ALL,1       Enciende LED 1 y LED 2 (100 %) juntos",
            "ALL,0       Apaga LED 1 y LED 2 juntos",
            "STATUS      Estado: LED, PWM, ADC %, BTN, SAMPLES, RAW",
            "TOGGLE      Invierte LED 1 (si esta prendido lo apaga)",
            "HELP        Muestra esta ayuda",
            "------------------------------------------------",
            "Boton (GP16): cada presion cambia BTN 0 <-> 1",
            "              y muestra EVENT + STATUS",
            "================================================",
        ])

    # BONUS: TOGGLE
    if cmd == "TOGGLE":
        if len(partes) != 1:
            return "ERR,BAD_FORMAT"
        with lock:
            nuevo = 0 if estado["led"] else 1
        set_led(nuevo)
        return "ACK,TOGGLE,{}".format(nuevo)

    # Desconocido 
    return "ERR,UNKNOWN_COMMAND"


def main():
    global corriendo

    # Estado inicial 
    set_led(0)
    set_pwm(0)

    # Core 1
    _thread.start_new_thread(tarea_core1, ())
    time.sleep(0.2)

    imprimir("Escribe HELP para ver comandos")

    # Core 0
    while True:
        try:
            linea = input()
            respuesta = procesar(linea)
            if respuesta:
                imprimir(respuesta)
        except KeyboardInterrupt:
            # Stop / Ctrl+C: apaga todo y detiene Core 1
            corriendo = False
            time.sleep(0.2)
            led_dig.value(0)
            led_pwm.duty_u16(0)
            imprimir("STOPPED")
            break                     # sale del while
        except Exception as e:
            # Error inesperado: avisamos y seguimos funcionando
            imprimir("ERR,INTERNAL,{}".format(e))

main()