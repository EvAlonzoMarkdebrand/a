"""
CYBER SMASH ARENA - Servidor Web y Multijugador Online para PythonAnywhere
==========================================================================
Este archivo implementa el backend WSGI completo para alojar partidas online.
Funciona tanto en PythonAnywhere (con Flask/WSGI) como localmente (con Flask o el servidor estándar WSGI).
"""

import time
import json
import random
import string
import os

# Almacén de salas en memoria
rooms = {}

def generate_room_code():
    chars = string.ascii_uppercase + "23456789"
    for _ in range(100):
        code = "CYBER-" + "".join(random.choices(chars, k=4))
        if code not in rooms:
            return code
    return "CYBER-" + str(random.randint(1000, 9999))

def clean_expired_rooms():
    now = time.time()
    expired = []
    for r_id, r in rooms.items():
        # Elimina salas inactivas por más de 10 minutos
        if now - r.get("last_activity", now) > 600:
            expired.append(r_id)
    for r_id in expired:
        rooms.pop(r_id, None)


# ==============================================================================
# LÓGICA DE API DEL SERVIDOR MULTIJUGADOR
# ==============================================================================
def api_status():
    clean_expired_rooms()
    return {
        "status": "online",
        "service": "Cyber Smash Arena Online Server",
        "active_rooms": len(rooms),
        "timestamp": time.time()
    }

def api_create_room(data):
    clean_expired_rooms()
    room_id = generate_room_code()
    stocks = data.get("stocks", 3) if data else 3
    stage = data.get("stage", "CYBER SKYPORT") if data else "CYBER SKYPORT"

    rooms[room_id] = {
        "id": room_id,
        "created_at": time.time(),
        "last_activity": time.time(),
        "stocks": stocks,
        "stage": stage,
        "p1_connected": True,
        "p2_connected": False,
        "p1_last_ping": time.time(),
        "p2_last_ping": 0,
        "p1_char": "NEXUS",
        "p2_char": "VALKYRIE",
        "p1_ready": False,
        "p2_ready": False,
        "match_started": False,
        "p1_state": None,
        "p2_state": None,
        "p1_events": [],
        "p2_events": []
    }

    return {
        "success": True,
        "room_id": room_id,
        "player": 1,
        "message": f"Sala {room_id} creada exitosamente."
    }

def api_join_room(data):
    clean_expired_rooms()
    if not data or "room_id" not in data:
        return {"success": False, "error": "Debes especificar room_id."}

    room_id = data["room_id"].strip().upper()
    if room_id not in rooms:
        return {"success": False, "error": f"La sala {room_id} no existe o ya expiró."}

    room = rooms[room_id]
    if room["p2_connected"] and (time.time() - room["p2_last_ping"] < 12):
        return {"success": False, "error": "La sala ya tiene 2 jugadores."}

    room["p2_connected"] = True
    room["p2_last_ping"] = time.time()
    room["last_activity"] = time.time()

    return {
        "success": True,
        "room_id": room_id,
        "player": 2,
        "stocks": room["stocks"],
        "stage": room["stage"],
        "message": f"Te has unido a la sala {room_id} como Jugador 2."
    }

def api_lobby_sync(room_id, data):
    clean_expired_rooms()
    room_id = room_id.strip().upper()
    if room_id not in rooms:
        return {"success": False, "error": "Sala no encontrada."}

    room = rooms[room_id]
    room["last_activity"] = time.time()
    player = data.get("player", 1)

    if player == 1:
        room["p1_last_ping"] = time.time()
        if "char" in data:
            room["p1_char"] = data["char"]
        if "ready" in data:
            room["p1_ready"] = bool(data["ready"])
        if "stocks" in data:
            room["stocks"] = data["stocks"]
    elif player == 2:
        room["p2_connected"] = True
        room["p2_last_ping"] = time.time()
        if "char" in data:
            room["p2_char"] = data["char"]
        if "ready" in data:
            room["p2_ready"] = bool(data["ready"])

    # Si ambos jugadores están listos, inicia el combate
    if room["p1_connected"] and room["p2_connected"] and room["p1_ready"] and room["p2_ready"]:
        room["match_started"] = True

    return {
        "success": True,
        "room_id": room_id,
        "p1_connected": room["p1_connected"],
        "p2_connected": (room["p2_connected"] and (time.time() - room["p2_last_ping"] < 12)),
        "p1_char": room["p1_char"],
        "p2_char": room["p2_char"],
        "p1_ready": room["p1_ready"],
        "p2_ready": room["p2_ready"],
        "stocks": room["stocks"],
        "stage": room["stage"],
        "match_started": room["match_started"]
    }

def api_game_sync(room_id, data):
    room_id = room_id.strip().upper()
    if room_id not in rooms:
        return {"success": False, "error": "Sala no encontrada."}

    room = rooms[room_id]
    now = time.time()
    room["last_activity"] = now
    player = data.get("player", 1)
    state = data.get("state")
    events = data.get("events", [])

    if player == 1:
        room["p1_last_ping"] = now
        if state is not None:
            room["p1_state"] = state
        if events:
            room["p1_events"].extend(events)
            room["p1_events"] = room["p1_events"][-20:]

        opponent_state = room["p2_state"]
        opponent_events = list(room["p2_events"])
        room["p2_events"].clear()
        opponent_active = (now - room["p2_last_ping"] < 8)
    else:
        room["p2_last_ping"] = now
        if state is not None:
            room["p2_state"] = state
        if events:
            room["p2_events"].extend(events)
            room["p2_events"] = room["p2_events"][-20:]

        opponent_state = room["p1_state"]
        opponent_events = list(room["p1_events"])
        room["p1_events"].clear()
        opponent_active = (now - room["p1_last_ping"] < 8)

    return {
        "success": True,
        "opponent_active": opponent_active,
        "opponent_state": opponent_state,
        "opponent_events": opponent_events,
        "timestamp": now
    }

def api_leave_room(room_id, data):
    room_id = room_id.strip().upper()
    if room_id in rooms:
        player = data.get("player", 1) if data else 1
        if player == 1:
            rooms.pop(room_id, None)
        else:
            rooms[room_id]["p2_connected"] = False
            rooms[room_id]["p2_ready"] = False
    return {"success": True, "message": "Saliste de la sala."}


# ==============================================================================
# ADAPTADOR FLASK (PREFERIDO PARA PYTHONANYWHERE)
# ==============================================================================
try:
    from flask import Flask, request, jsonify, render_template, send_from_directory

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Cabeceras CORS abiertas para permitir peticiones web y cliente de escritorio
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    @app.route("/")
    def index():
        template_path = os.path.join(app.template_folder, "index.html")
        if os.path.exists(template_path):
            return render_template("index.html")
        return jsonify({
            "status": "online",
            "title": "CYBER SMASH ARENA - PythonAnywhere Server",
            "message": "Servidor en línea y listo para recibir jugadores de Pygame y Web.",
            "endpoints": [
                "/api/status",
                "/api/create_room",
                "/api/join_room",
                "/api/room/<id>/lobby",
                "/api/room/<id>/sync"
            ]
        })

    @app.route("/api/status", methods=["GET"])
    def route_status():
        return jsonify(api_status())

    @app.route("/api/create_room", methods=["POST", "OPTIONS"])
    def route_create_room():
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"})
        data = request.get_json(silent=True) or {}
        return jsonify(api_create_room(data))

    @app.route("/api/join_room", methods=["POST", "OPTIONS"])
    def route_join_room():
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"})
        data = request.get_json(silent=True) or {}
        return jsonify(api_join_room(data))

    @app.route("/api/room/<room_id>/lobby", methods=["POST", "OPTIONS"])
    def route_lobby(room_id):
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"})
        data = request.get_json(silent=True) or {}
        return jsonify(api_lobby_sync(room_id, data))

    @app.route("/api/room/<room_id>/sync", methods=["POST", "OPTIONS"])
    def route_sync(room_id):
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"})
        data = request.get_json(silent=True) or {}
        return jsonify(api_game_sync(room_id, data))

    @app.route("/api/room/<room_id>/leave", methods=["POST", "OPTIONS"])
    def route_leave(room_id):
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"})
        data = request.get_json(silent=True) or {}
        return jsonify(api_leave_room(room_id, data))

    HAVE_FLASK = True

except ImportError:
    HAVE_FLASK = False
    app = None


# ==============================================================================
# ADAPTADOR WSGI ESTÁNDAR (Para compatibilidad universal y prueba local sin pip)
# ==============================================================================
def standard_wsgi_app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # Manejar OPTIONS para CORS
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ]
        start_response("200 OK", headers)
        return [b"{}"]

    data = {}
    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            if length > 0:
                body = environ["wsgi.input"].read(length)
                data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

    headers = [
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
    ]

    res = {}
    if path == "/" or path == "/api/status":
        res = api_status()
    elif path == "/api/create_room":
        res = api_create_room(data)
    elif path == "/api/join_room":
        res = api_join_room(data)
    elif path.startswith("/api/room/") and path.endswith("/lobby"):
        parts = path.strip("/").split("/")
        if len(parts) >= 4:
            res = api_lobby_sync(parts[2], data)
    elif path.startswith("/api/room/") and path.endswith("/sync"):
        parts = path.strip("/").split("/")
        if len(parts) >= 4:
            res = api_game_sync(parts[2], data)
    elif path.startswith("/api/room/") and path.endswith("/leave"):
        parts = path.strip("/").split("/")
        if len(parts) >= 4:
            res = api_leave_room(parts[2], data)
    else:
        start_response("404 Not Found", headers)
        return [json.dumps({"error": "Ruta no encontrada"}).encode("utf-8")]

    start_response("200 OK", headers)
    return [json.dumps(res).encode("utf-8")]


# En PythonAnywhere, el servidor WSGI busca una variable llamada `application` o `app`
application = app if HAVE_FLASK else standard_wsgi_app


# ==============================================================================
# EJECUCIÓN DIRECTA (Servidor de pruebas local)
# ==============================================================================
if __name__ == "__main__":
    PORT = 5000
    print("=" * 70)
    print("  CYBER SMASH ARENA - SERVIDOR MULTIJUGADOR")
    print(f"  Iniciando servidor en http://127.0.0.1:{PORT}")
    print("=" * 70)

    if HAVE_FLASK:
        print("-> Modo: Flask Web Server")
        app.run(host="0.0.0.0", port=PORT, debug=True)
    else:
        from wsgiref.simple_server import make_server
        print("-> Modo: Standard Library WSGI Server (Sin dependencias externas)")
        httpd = make_server("0.0.0.0", PORT, standard_wsgi_app)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
