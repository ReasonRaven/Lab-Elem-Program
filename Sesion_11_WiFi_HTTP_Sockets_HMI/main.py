# =====================================================================
# DO11 - Smart Wi-Fi HMI FINAL
# Laboratorio de Elementos Programables - Sesion 11
# Raspberry Pi Pico 2 W (MicroPython)
#
# - Pico en modo STA (mismo Wi-Fi que la laptop)
# - Slider web 0-100 %  -> LED PWM en GP15
# - Boton TOGGLE        -> LED2 en GP14
# - OLED I2C GP4/GP5    -> IP, PWM, LED2, requests
# - API: /api/pwm?value=N, /api/led2/toggle, /api/status
# - Errores 400 / 404 sin detener el servidor
# - Content-Length + Connection: close
#
# Archivos en la RAIZ de la Pico:  main.py, secrets.py, ssd1306.py
# =====================================================================

import network
import socket
import errno
import json
from machine import Pin, PWM, I2C
from time import sleep_ms, ticks_ms, ticks_diff

from secrets_template import WIFI_SSID, WIFI_PASSWORD   # NO se sube a GitHub

# ---------------------------------------------------------------------
# CONFIGURACION DE HARDWARE
# ---------------------------------------------------------------------
PWM_PIN = 15
LED2_PIN = 14
I2C_SDA = 4
I2C_SCL = 5
OLED_W = 128
OLED_H = 64

led_pwm = PWM(Pin(PWM_PIN))
led_pwm.freq(1000)
led_pwm.duty_u16(0)

led2 = Pin(LED2_PIN, Pin.OUT, value=0)

# Estado global del sistema (lo mismo que muestra la OLED y la API)
state = {
    "ip": "0.0.0.0",
    "pwm": 0,
    "led2": 0,
    "requests": 0,
}

# ---------------------------------------------------------------------
# OLED (si falla, el dashboard sigue funcionando)
# ---------------------------------------------------------------------
oled = None


def init_oled():
    global oled
    try:
        import ssd1306
        i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400000)
        found = i2c.scan()
        print("I2C scan:", [hex(a) for a in found])
        if not found:
            print("OLED no detectada: revisa SDA/SCL/VCC/GND")
            return
        oled = ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)
        print("OLED lista")
    except Exception as exc:
        oled = None
        print("OLED deshabilitada:", exc)


def oled_message(lines):
    if oled is None:
        return
    try:
        oled.fill(0)
        y = 0
        for line in lines:
            oled.text(str(line)[:16], 0, y)
            y += 12
        oled.show()
    except Exception as exc:
        print("Error OLED:", exc)


def update_oled():
    oled_message([
        "WIFI DASHBOARD",
        state["ip"],
        "PWM: {}%".format(state["pwm"]),
        "LED2: {}".format("ON" if state["led2"] else "OFF"),
        "REQ: {}".format(state["requests"]),
    ])


# ---------------------------------------------------------------------
# ACTUADORES
# ---------------------------------------------------------------------
def set_pwm(percent):
    percent = max(0, min(100, int(percent)))
    duty = int(percent * 65535 / 100)
    led_pwm.duty_u16(duty)
    state["pwm"] = percent
    return duty


def toggle_led2():
    new_value = 0 if led2.value() else 1
    led2.value(new_value)
    state["led2"] = new_value


# ---------------------------------------------------------------------
# WI-FI (modo STA)
# ---------------------------------------------------------------------
def get_sta_interface():
    try:
        return network.WLAN(network.WLAN.IF_STA)
    except AttributeError:
        return network.WLAN(network.STA_IF)


def connect_wifi(ssid, password, timeout_ms=20000):
    wlan = get_sta_interface()
    wlan.active(True)

    if wlan.isconnected():
        print("Wi-Fi ya conectado, IP:", wlan.ifconfig()[0])
        return wlan

    try:
        wlan.disconnect()
        sleep_ms(200)
    except Exception:
        pass

    print("Conectando a:", ssid)
    oled_message(["Conectando...", ssid])
    wlan.connect(ssid, password)

    start = ticks_ms()
    last_status = None

    while not wlan.isconnected():
        status = wlan.status()
        if status != last_status:
            print("Wi-Fi status:", status)
            last_status = status

        if status < 0:
            raise RuntimeError(
                "Fallo de conexion, status={}. "
                "Revisa SSID, password y 2.4 GHz.".format(status))

        if ticks_diff(ticks_ms(), start) >= timeout_ms:
            raise RuntimeError(
                "Timeout de conexion, status={}.".format(status))

        sleep_ms(250)

    print("Wi-Fi conectado, IP:", wlan.ifconfig()[0])
    return wlan


# ---------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------
def create_server(port=80):
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    server = socket.socket()
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    server.bind(addr)
    server.listen(2)
    server.settimeout(1)          # accept() regresa cada 1 s
    return server


def send_response(client, body, content_type="text/html; charset=utf-8",
                  status="200 OK"):
    if isinstance(body, str):
        body = body.encode()
    header = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "Cache-Control: no-store\r\n"
        "\r\n"
    ).format(status, content_type, len(body))
    client.sendall(header.encode())
    if body:
        client.sendall(body)


def send_json(client, data, status="200 OK"):
    send_response(client, json.dumps(data),
                  "application/json", status)


def send_error(client, code, message):
    reason = {400: "Bad Request", 404: "Not Found",
              405: "Method Not Allowed"}.get(code, "Error")
    send_json(client, {"error": message, "code": code},
              "{} {}".format(code, reason))


def parse_query(query):
    params = {}
    if not query:
        return params
    for pair in query.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
        else:
            key, value = pair, ""
        params[key] = value
    return params


def parse_percent(text):
    """Regresa un entero 0-100, o None si el valor es invalido."""
    if text is None or text == "":
        return None
    if not text.isdigit():        # rechaza "-5", "abc", "12.5"
        return None
    value = int(text)
    if value < 0 or value > 100:
        return None
    return value


def is_timeout(exc):
    code = exc.args[0] if exc.args else None
    return code in (errno.ETIMEDOUT, 110)


# ---------------------------------------------------------------------
# DASHBOARD HTML (estatico; los datos llegan por /api/status)
# ---------------------------------------------------------------------
DASHBOARD = """<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Wi-Fi HMI</title>
<style>
body{font-family:Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}
.card{max-width:460px;margin:0 auto 16px;background:#1e293b;border-radius:12px;padding:18px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0 0 12px;color:#94a3b8}
input[type=range]{width:100%}
.big{font-size:32px;font-weight:bold;text-align:center;margin:8px 0}
.row{display:flex;gap:6px;flex-wrap:wrap}
button{flex:1;padding:10px;border:0;border-radius:8px;background:#3b82f6;color:#fff;font-size:15px;cursor:pointer}
button.t{background:#64748b;width:100%;font-size:18px}button.on{background:#22c55e}
table{width:100%}td{padding:4px 0}td:last-child{text-align:right;font-weight:bold}
#msg{min-height:18px;color:#f87171;text-align:center}
a{color:#93c5fd}
</style></head><body>
<div class="card"><h1>Smart Wi-Fi HMI</h1><h2>Pico 2 W - DO11</h2></div>

<div class="card"><h2>LED PWM (GP15)</h2>
<div class="big" id="v">0 %</div>
<input type="range" id="s" min="0" max="100" value="0">
<div class="row" style="margin-top:10px">
<button onclick="setp(0)">OFF</button><button onclick="setp(25)">25%</button>
<button onclick="setp(50)">50%</button><button onclick="setp(75)">75%</button>
<button onclick="setp(100)">100%</button></div></div>

<div class="card"><h2>LED2 (GP14)</h2>
<button class="t" id="b" onclick="call('/api/led2/toggle')">TOGGLE - OFF</button></div>

<div class="card"><h2>Estado</h2><table>
<tr><td>IP</td><td id="ip">-</td></tr>
<tr><td>PWM</td><td id="pw">-</td></tr>
<tr><td>LED2</td><td id="l2">-</td></tr>
<tr><td>Requests</td><td id="rq">-</td></tr></table>
<p id="msg"></p><p><a href="/api/status" target="_blank">/api/status (JSON)</a></p></div>

<script>
var s=document.getElementById('s'),v=document.getElementById('v'),drag=false;
function el(i){return document.getElementById(i)}
function show(d){
 el('ip').textContent=d.ip;el('pw').textContent=d.pwm+' %';
 el('l2').textContent=d.led2?'ON':'OFF';el('rq').textContent=d.requests;
 if(!drag){s.value=d.pwm;v.textContent=d.pwm+' %'}
 var b=el('b');b.textContent='TOGGLE - '+(d.led2?'ON':'OFF');
 b.className=d.led2?'t on':'t';el('msg').textContent='';
}
function call(u){
 fetch(u).then(function(r){return r.json().then(function(d){
  if(r.ok){show(d)}else{el('msg').textContent='Error '+d.code+': '+d.error}
 })}).catch(function(){el('msg').textContent='Sin conexion con la Pico'});
}
function setp(p){s.value=p;v.textContent=p+' %';call('/api/pwm?value='+p)}
s.oninput=function(){drag=true;v.textContent=s.value+' %'};
s.onchange=function(){drag=false;call('/api/pwm?value='+s.value)};
call('/api/status');
setInterval(function(){if(!drag)call('/api/status')},5000);
</script></body></html>"""


# ---------------------------------------------------------------------
# RUTEO
# ---------------------------------------------------------------------
def route(client, method, path, query):
    if method != "GET":
        send_error(client, 405, "Solo se acepta GET")
        return

    if path == "/":
        send_response(client, DASHBOARD)

    elif path == "/api/status":
        send_json(client, state)

    elif path == "/api/pwm":
        params = parse_query(query)
        value = parse_percent(params.get("value"))
        if value is None:
            send_error(client, 400,
                       "value debe ser un entero entre 0 y 100")
            return
        set_pwm(value)
        send_json(client, state)

    elif path == "/api/led2/toggle":
        toggle_led2()
        send_json(client, state)

    elif path.startswith("/pwm/"):
        # Botones fijos de SHOW 4: /pwm/0, /pwm/25, /pwm/50 ...
        value = parse_percent(path[5:])
        if value is None:
            send_error(client, 400,
                       "porcentaje invalido, usa 0 a 100")
            return
        set_pwm(value)
        send_json(client, state)

    elif path == "/favicon.ico":
        send_response(client, b"", "image/x-icon", "204 No Content")

    else:
        send_error(client, 404, "Ruta no encontrada: " + path)


def handle_client(client):
    client.settimeout(3)
    raw = client.recv(1024)
    if not raw:                    # conexion vacia (preconnect de Chrome)
        return

    try:
        first_line = raw.split(b"\r\n", 1)[0].decode()
    except Exception:
        send_error(client, 400, "Peticion ilegible")
        return

    parts = first_line.split(" ")
    if len(parts) < 2:
        send_error(client, 400, "Peticion HTTP mal formada")
        return

    method, target = parts[0], parts[1]
    if "?" in target:
        path, query = target.split("?", 1)
    else:
        path, query = target, ""

    state["requests"] += 1
    print("#{} {} {}".format(state["requests"], method, target))

    route(client, method, path, query)
    update_oled()


# ---------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------
init_oled()
oled_message(["DO11 Smart HMI", "Iniciando..."])

try:
    wlan = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
except Exception as exc:
    print("ERROR WI-FI:", exc)
    oled_message(["ERROR WI-FI", "Revisa secrets", "y red 2.4 GHz"])
    raise

state["ip"] = wlan.ifconfig()[0]
set_pwm(0)
update_oled()

server = create_server(80)

print()
print("==============================")
print(" SMART WI-FI HMI LISTO (DO11)")
print("==============================")
print(" Dashboard: http://{}/".format(state["ip"]))
print(" API:       http://{}/api/status".format(state["ip"]))
print()

last_wait = ticks_ms()

while True:
    client = None
    try:
        client, remote = server.accept()
        handle_client(client)

    except OSError as exc:
        if client is None and is_timeout(exc):
            if ticks_diff(ticks_ms(), last_wait) >= 5000:
                print("Esperando navegador en http://{}/ ...".format(
                    state["ip"]))
                last_wait = ticks_ms()
        else:
            print("Error de socket:", exc)

    except Exception as exc:
        # Cualquier error inesperado se reporta, pero el servidor sigue
        print("SERVER ERROR:", exc)
        try:
            if client:
                send_error(client, 400, "Error procesando la peticion")
        except Exception:
            pass

    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass