from machine import Pin, Timer
from time import ticks_ms, ticks_diff, sleep_ms
from random import randint

LED_SIGNAL = Pin(15, Pin.OUT)
LED_WAIT = Pin(14, Pin.OUT)
BUTTON = Pin(16, Pin.IN, Pin.PULL_UP)

STATE_WAITING = 0
STATE_READY = 1
STATE_DONE = 2

state = STATE_DONE
start_ms = 0
reaction_ms = 0
result_ready = False
false_start = False
last_irq_ms = 0
round_number = 0

timer = Timer(-1)


def show_signal(t):
    global state, start_ms
    LED_SIGNAL.on()
    LED_WAIT.off()
    start_ms = ticks_ms()
    state = STATE_READY


def schedule_round():
    global state, result_ready, false_start, round_number
    round_number += 1
    LED_SIGNAL.off()
    LED_WAIT.on()
    result_ready = False
    false_start = False
    state = STATE_WAITING

    delay_ms = randint(1000, 10000)
    print("\n============================")
    print("Round", round_number)
    print("Espera la señal visual. No presiones antes.")
    print("Delay aleatorio:", delay_ms, "ms")
    print("=================================")

    timer.init(mode=Timer.ONE_SHOT, period=delay_ms, callback=show_signal)


def button_irq(pin):
    global state, reaction_ms, result_ready, false_start, last_irq_ms

    now = ticks_ms()

    if ticks_diff(now, last_irq_ms) < 80:
        return
    last_irq_ms = now

    if state == STATE_READY:
        reaction_ms = ticks_diff(now, start_ms)
        LED_SIGNAL.off()
        result_ready = True
        state = STATE_DONE

    elif state == STATE_WAITING:
        timer.deinit()
        false_start = True
        result_ready = True
        state = STATE_DONE


BUTTON.irq(trigger=Pin.IRQ_FALLING, handler=button_irq)

print("JUEGO DE LOS REFLEJOS")

schedule_round()  

while True:
    if result_ready:
        if false_start:
            print("SALIDA EN FALSO: presionaste antes de la señal")
        else:
            print("Tiempo de reaccion: ", reaction_ms, "ms")

        sleep_ms(1800)

        while BUTTON.value() == 0:
            sleep_ms(10)

        schedule_round()

    sleep_ms(20)