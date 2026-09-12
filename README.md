# Laboratorio de Elementos Programables

Repositorio de tareas, prácticas y evidencias del laboratorio de **Elementos Programables** (5º semestre).

**Autor:** Jonathan Hernández Lazcano — 200417

## Contenido

| Sesión | Tema | Entregables |
|--------|------|-------------|
| [Sesión 02](Sesion_02_Conceptos_Basicos_MCU/) | Conceptos básicos de microcontroladores | Infografía (PDF) |
| [Sesión 03](Sesion_03_GPIO_Pullup_Pulldown/) | GPIO con pull-up / pull-down | Código MicroPython, simulación Wokwi, armado físico, video |
| [Sesión 04](Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/) | Interrupciones y temporizadores | Código MicroPython, diagrama Wokwi, armado físico, evidencia |

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

| Elemento | Pin GPIO |
|----------|----------|
| LED de señal | 15 |
| LED de espera | 14 |
| Botón | 16 (`PULL_UP`) |

## Hardware y herramientas

- **Placa:** Raspberry Pi Pico (RP2040)
- **Firmware:** MicroPython v1.28.0
- **Simulador:** [Wokwi](https://wokwi.com/)
- **Componentes:** LEDs, resistencias de 330 Ω y botones pulsadores


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
└── Sesion_04_Interrupciones_Temporizadores_FINAL_SIMULABLE/
    ├── Evidencia/
    └── Wokwi_Micropython/
```

Las Sesiones 03 y 04 incluyen además su propio `README.md` con objetivo, tabla de pines, funcionamiento, pruebas y conclusiones.

