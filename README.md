# Laboratorio de Elementos Programables

Repositorio de tareas, prácticas y evidencias del laboratorio de **Elementos Programables** (5º semestre).

**Autor:** Jonathan Hernández Lazcano — 200417

> Las Sesiones 07, 08 y 09 se realizaron en equipo con Camila Rodriguez Rosas.

## Contenido

| Sesión | Tema | Entregables |
|--------|------|-------------|
| [Sesión 02](Sesion_02_Conceptos_Basicos_MCU/) | Conceptos básicos de microcontroladores | Infografía (PDF) |
| [Sesión 03](Sesion_03_GPIO_Pullup_Pulldown/) | GPIO con pull-up / pull-down | Código MicroPython, simulación Wokwi, armado físico, video |
| [Sesión 04](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/) | Interrupciones y temporizadores | Código MicroPython, diagrama Wokwi, armado físico, evidencia, video |
| [Sesión 06](Sesion_06_PWM_Motor_DC/) | PWM + puente H L298N + motor DC | Código MicroPython (modo auto y manual), simulación Wokwi, armado físico, videos |
| [Sesión 07](Sesion_07_ADC_Signal_Conditioning/) | ADC y acondicionamiento de señal (Smart Analog Monitor) | Código MicroPython, simulación Wokwi, armado físico, evidencia, videos |
| [Sesión 08](Sesion_08_Dual_Core_Multitarea/) | Multitarea cooperativa y dual core | Código MicroPython, simulación Wokwi, armado físico, video |
| [Sesión 09](Sesion_09_Comunicacion_UART/) | Comunicación UART (UART Command Center) | Código MicroPython, tabla de pruebas, exit ticket, armado físico, video |

## Descripción de las sesiones

### Sesión 02 — Conceptos básicos de MCU
Infografía con los conceptos fundamentales de microcontroladores: arquitectura, memorias, periféricos y diferencias frente a un microprocesador.

- [`infographic/Hernández_Jonathan_S02_Infografia.pdf`](Sesion_02_Conceptos_Basicos_MCU/infographic/)

### Sesión 03 — GPIO Pull-up / Pull-down
Semáforo vehicular y peatonal controlado por un botón configurado con la **resistencia de pull-up interna** (`Pin.PULL_UP`), con antirrebote por software. Se validó tanto en simulación como en hardware real.

- [`py/semaforo_PULL_UP.py`](Sesion_03_GPIO_Pullup_Pulldown/py/semaforo_PULL_UP.py) — programa principal
- [`wokwi/evidence/`](Sesion_03_GPIO_Pullup_Pulldown/wokwi/evidence/) — capturas de la simulación y del circuito armado
- [Video de la práctica](https://youtu.be/GcFuO7eJdIo)
- Detalles completos en el [README de la sesión](Sesion_03_GPIO_Pullup_Pulldown/README.md)

### Sesión 04 — Interrupciones y temporizadores
Juego de reflejos: tras un retardo aleatorio (1–10 s) generado con un `Timer` en modo `ONE_SHOT` se enciende un LED de señal, y el tiempo de reacción se mide dentro de una **interrupción por flanco de bajada** del botón. Detecta salidas en falso si se presiona antes de la señal.

- [`Wokwi_Micropython/Reaction_Game.py`](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/Wokwi_Micropython/Reaction_Game.py) — programa principal
- [`Wokwi_Micropython/Diagrama.json`](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/Wokwi_Micropython/Diagrama.json) — circuito para Wokwi
- [`Evidencia/`](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/Evidencia/) — diagrama del circuito, armado físico y monitor serie
- [Video de la práctica](https://youtube.com/shorts/Winyt-tXFpY)

| Elemento | Pin GPIO |
|----------|----------|
| LED de señal | 15 |
| LED de espera | 14 |
| Botón | 16 (`PULL_UP`) |

- Detalles completos en el [README de la sesión](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/README.md)

### Sesión 06 — PWM + Puente H L298N + Motor DC
*Smart Motor Controller*: control de un motor DC a través de un puente H **L298N**. `IN1`/`IN2` fijan la dirección y `ENA` recibe una señal **PWM a 1 kHz** (`duty_u16`) que regula la velocidad. Incluye rampas de aceleración/desaceleración y un **cambio seguro de dirección** (siempre pasa por 0 % antes de invertir el giro).

- **Modo AUTO (reto base):** prueba de velocidades 25/50/75/100 % y ciclo FORWARD 0 → 100 % → cambio seguro → REVERSE 0 → 75 % → STOP.
- **Modo MANUAL (bonus):** botones FORWARD / REVERSE / STOP con interrupciones y debounce de 150 ms, y un potenciómetro (ADC0) que fija la velocidad objetivo con una rampa no bloqueante.

- [`PWM_AUTO.py`](Sesion_06_PWM_Motor_DC/PWM_AUTO.py) — programa con `MODO = "AUTO"`
- [`PWM_MANUAL.PY`](Sesion_06_PWM_Motor_DC/PWM_MANUAL.PY) — programa con `MODO = "MANUAL"`
- [`wokwi/diagram.json`](Sesion_06_PWM_Motor_DC/wokwi/diagram.json) — circuito para Wokwi ([proyecto en línea](https://wokwi.com/projects/476185998157129729))
- [`evidence/`](Sesion_06_PWM_Motor_DC/evidence/) — captura de la simulación y fotos del montaje físico
- Videos: [modo AUTO](https://youtube.com/shorts/xu2d1WG4CZY?feature=share) · [modo MANUAL](https://youtube.com/shorts/6QihC__thcQ?feature=share)
- Detalles completos en el [README de la sesión](Sesion_06_PWM_Motor_DC/README.md)

| Elemento | Pin GPIO |
|----------|----------|
| IN1 / IN2 (dirección) | 2 / 3 |
| ENA (PWM, velocidad) | 4 |
| Botones FORWARD / REVERSE / STOP | 14 / 15 / 16 (`PULL_UP`) |
| Potenciómetro | 26 (ADC0) |

### Sesión 07 — Conversión ADC y acondicionamiento de señal
*Smart Analog Monitor*: lectura de una señal analógica con `read_u16()` (0–65535), conversión a voltaje y porcentaje, **filtro de promedio móvil** para eliminar ruido y clasificación en tres estados (**NORMAL / WARNING / ALARM**) mostrados con LEDs y por serial. El sensor activo (potenciómetro en GP26 o LDR con divisor de voltaje en GP27) se elige en el código.

- [`main.py`](Sesion_07_ADC_Signal_Conditioning/main.py) — programa principal
- [`wokwi/`](Sesion_07_ADC_Signal_Conditioning/wokwi/) — circuito y enlace de la simulación
- [`evidence/`](Sesion_07_ADC_Signal_Conditioning/evidence/) — lecturas seriales y fotos del montaje
- Detalles completos en el [README de la sesión](Sesion_07_ADC_Signal_Conditioning/README.md)

| Elemento | Pin GPIO |
|----------|----------|
| Potenciómetro | 26 (ADC0) |
| LDR + 10 kΩ (divisor) | 27 (ADC1) |
| LED verde / amarillo / rojo | 13 / 14 / 15 |

### Sesión 08 — Multitarea cooperativa y dual core
*Challenge 08*: monitor analógico con **planificador cooperativo** en un solo núcleo (sin `_thread`) basado en `ticks_ms`. Cuatro tareas periódicas: sensor (2 ms, promedio móvil de 32 muestras con **auto-calibración** del rango del potenciómetro), botón (10 ms, antirrebote; pulsación corta = ACK, larga = RESET), UI de LEDs (200 ms) y log serial (1 s). `STRESS_BLOCK_MS` permite una prueba de estrés para comparar contra una versión dual-core.

- [`main.py`](Sesion_08_Dual_Core_Multitarea/main.py) — programa principal
- [`wokwi/diagram.json`](Sesion_08_Dual_Core_Multitarea/wokwi/diagram.json) — circuito para Wokwi ([proyecto en línea](https://wokwi.com/projects/477453120162961409))
- [`evidence/`](Sesion_08_Dual_Core_Multitarea/evidence/) — foto del armado físico
- [Video del armado](https://youtube.com/shorts/y9N-Xi04YrA?feature=share)
- Detalles completos en el [README de la sesión](Sesion_08_Dual_Core_Multitarea/README.md)

| Elemento | Pin GPIO |
|----------|----------|
| Potenciómetro | 26 (ADC0) |
| LED verde / amarillo / rojo / azul (heartbeat) | 16 / 17 / 18 / 19 |
| Botón (ACK / RESET) | 20 (`PULL_UP`) |

### Sesión 09 — Comunicación UART
*Challenge 09 · UART Command Center*: el operador escribe comandos en la terminal (USB/REPL), el programa los transmite por el **UART0 físico** (9600 baud, 8N1) y los recibe de vuelta mediante un **jumper de loopback GP0 (TX) → GP1 (RX)**. Un parser interpreta la trama `COMANDO,ARG1,ARG2\n`, controla dos LEDs y responde siempre con `ACK`, `ERR` o `STATUS`. Soporta `PING`, `SET`, `GET,STATUS`, `TOGGLE`, `BLINK` (con `Timer`, no bloqueante) y `HELP`, con validación de campos, dispositivo y valor. Las 8 pruebas de la tabla resultaron PASS.

- [`main.py`](Sesion_09_Comunicacion_UART/main.py) — programa principal
- [`tabla_pruebas.csv`](Sesion_09_Comunicacion_UART/tabla_pruebas.csv) — tabla de pruebas (8/8 PASS)
- [`evidencia/`](Sesion_09_Comunicacion_UART/evidencia/) — foto del armado físico y captura de la terminal
- [Video de la prueba física](https://youtube.com/shorts/psTezm2v7y4)
- Detalles completos en el [README de la sesión](Sesion_09_Comunicacion_UART/README.md)

| Elemento | Pin GPIO |
|----------|----------|
| UART0 TX → RX (jumper loopback) | 0 → 1 |
| LED1 / LED2 | 13 / 14 |

## Hardware y herramientas

- **Placa:** Raspberry Pi Pico (RP2040); Pico W en el montaje físico de la Sesión 08 y Pico 2 W (RP2350) en la Sesión 09
- **Firmware:** MicroPython v1.28.0
- **Simulador:** [Wokwi](https://wokwi.com/)
- **Componentes:** LEDs, resistencias (220 Ω / 330 Ω), botones pulsadores, potenciómetro, LDR, puente H L298N y motor DC


## Estructura del repositorio

```
Lab-Elem-Program/
├── LICENSE
├── README.md
├── Sesion_02_Conceptos_Basicos_MCU/
│   └── infographic/
├── Sesion_03_GPIO_Pullup_Pulldown/
│   ├── py/
│   └── wokwi/evidence/
├── Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/
│   ├── Evidencia/
│   └── Wokwi_Micropython/
├── Sesion_06_PWM_Motor_DC/
│   ├── PWM_AUTO.py
│   ├── PWM_MANUAL.PY
│   ├── evidence/
│   └── wokwi/
├── Sesion_07_ADC_Signal_Conditioning/
│   ├── main.py
│   ├── evidence/
│   └── wokwi/
├── Sesion_08_Dual_Core_Multitarea/
│   ├── main.py
│   ├── evidence/
│   └── wokwi/
└── Sesion_09_Comunicacion_UART/
    ├── main.py
    ├── tabla_pruebas.csv
    └── evidencia/
```

Cada sesión incluye además su propio `README.md`; los de las Sesiones 03, 04, 06, 07, 08 y 09 detallan objetivo, tabla de pines, funcionamiento, pruebas y conclusiones.

