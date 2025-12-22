import time
import json
import network
import socket

from machine import Pin
import dht

# ====== CONFIG ======
# WIFI_SSID = "iPhone"
# WIFI_PASS = "KhalilEsp32"

WIFI_SSID = "FRITZ!Box 7530 PQ"
WIFI_PASS = "41120895611457227941"


DHT_PIN = 14          # <-- put your GPIO number here (e.g. 13)
DHT_TYPE = "DHT11"     # keep as DHT11
HTTP_PORT = 80

# DHT11 should not be polled too fast
MIN_SAMPLE_MS = 2000
# ====================

sensor = dht.DHT11(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))

_last = {"ts": 0, "t": None, "h": None, "err": None}

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        # wait up to ~15s
        for _ in range(150):
            if wlan.isconnected():
                break
            time.sleep(0.1)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WiFi connected. IP:", ip)
        return ip
    else:
        print("WiFi NOT connected.")
        return None

def read_dht_cached():
    now = time.ticks_ms()
    if time.ticks_diff(now, _last["ts"]) < MIN_SAMPLE_MS and _last["err"] is None:
        return _last

    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        _last["ts"] = now
        _last["t"] = t
        _last["h"] = h
        _last["err"] = None
    except Exception as e:
        _last["ts"] = now
        _last["err"] = str(e)

    return _last

def http_response(body, status="200 OK", content_type="application/json"):
    b = body if isinstance(body, (bytes, bytearray)) else body.encode("utf-8")
    headers = (
        "HTTP/1.1 " + status + "\r\n"
        "Content-Type: " + content_type + "\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Content-Length: " + str(len(b)) + "\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + b

def handle_client(cl):
    try:
        req = cl.recv(1024) or b""
        req_line = req.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
        parts = req_line.split()
        path = parts[1] if len(parts) >= 2 else "/"

        if path == "/" or path.startswith("/health"):
            body = json.dumps({"ok": True, "uptime_ms": time.ticks_ms()})
            cl.send(http_response(body))
            return

        if path.startswith("/api/dht"):
            r = read_dht_cached()
            if r["err"] is not None:
                body = json.dumps({"ok": False, "error": r["err"]})
                cl.send(http_response(body, status="503 Service Unavailable"))
                return

            body = json.dumps({
                "ok": True,
                "temperature_c": r["t"],
                "humidity_percent": r["h"],
                "sample_age_ms": time.ticks_diff(time.ticks_ms(), r["ts"]),
                "uptime_ms": time.ticks_ms(),
            })
            cl.send(http_response(body))
            return

        cl.send(http_response(json.dumps({"ok": False, "error": "not found"}), status="404 Not Found"))

    finally:
        try:
            cl.close()
        except:
            pass

def serve_forever():
    addr = socket.getaddrinfo("0.0.0.0", HTTP_PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("HTTP server listening on port", HTTP_PORT)

    while True:
        cl, _ = s.accept()
        handle_client(cl)

wifi_connect()
serve_forever()
