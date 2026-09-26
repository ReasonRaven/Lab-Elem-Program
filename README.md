# Laboratorio de Elementos Programables

Repositorio de tareas, prácticas y evidencias del laboratorio de **Elementos Programables** (5º semestre).

**Autor:** Jonathan Hernández Lazcano — 200417

## Contenido

| Sesión | Tema | Entregables |
|--------|------|-------------|
| [Sesión 02](Sesion_02_Conceptos_Basicos_MCU/) | Conceptos básicos de microcontroladores | Infografía (PDF) |
| [Sesión 03](Sesion_03_GPIO_Pullup_Pulldown/) | GPIO con pull-up / pull-down | Código MicroPython, simulación Wokwi, armado físico, video |
| [Sesión 04](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/) | Interrupciones y temporizadores | Código MicroPython, diagrama Wokwi, armado físico, evidencia, video |
| [Sesión 06](Sesion_06_PWM_Motor_DC/) | PWM + puente H L298N + motor DC | Código MicroPython (modo auto y manual), simulación Wokwi, armado físico, videos |

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

## Hardware y herramientas

- **Placa:** Raspberry Pi Pico (RP2040)
- **Firmware:** MicroPython v1.28.0
- **Simulador:** [Wokwi](https://wokwi.com/)
- **Componentes:** LEDs, resistencias de 330 Ω, botones pulsadores, potenciómetro, puente H L298N y motor DC


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
└── Sesion_06_PWM_Motor_DC/
    ├── PWM_AUTO.py
    ├── PWM_MANUAL.PY
    ├── evidence/
    └── wokwi/
```

Cada sesión incluye además su propio `README.md`; los de las Sesiones 03, 04 y 06 detallan objetivo, tabla de pines, funcionamiento, pruebas y conclusiones.

