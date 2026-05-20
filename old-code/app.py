from flask import Flask, jsonify, send_from_directory, Response, stream_with_context
import serial
import threading
import time
import queue
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log=logging.getLogger(__name__)

BASE_DIR=Path(__file__).resolve().parent
DIST_DIR=BASE_DIR/"gui-user"/"dist"

app=Flask(__name__, static_folder=str(DIST_DIR), static_url_path="/assets")
USER_PORTS={
    "matteo": ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"],
    "mike": ["COM3"],
}
def connect_arduino():
    for user, ports in USER_PORTS.items():
        for port in ports:
            try:
                # Try connection
                conn = serial.Serial(port=port, baudrate=9600, timeout=1)
                time.sleep(2) 
                log.info(f"Connected to {user}'s port: {port} ({user})")
                return conn
            except (serial.SerialException, OSError):
                continue
    log.warning("Arduino not found - running offline")
    return None

arduino=connect_arduino()
_serial_lock=threading.Lock()

def send_serial(cmd: str):
    if not arduino or not arduino.is_open:
        log.warning(f"Serial unavailable - dropped: {cmd}")
        return False
    try:
        with _serial_lock:
            arduino.write(f"{cmd}\n".encode())
        log.info(f"-> {cmd}")
        return True
    except serial.SerialException as e:
        log.error(f"Serial write error: {e}")
        return False

_lock=threading.Lock()
sensor_data={
    "temperature": "--",
    "humidity": "--",
    "light": "--",
    "distance": "--",
}

_state_lock=threading.Lock()
ROOM_ORDER=["entry", "hall", "bath", "bedroom", "ensuite", "kitchen", "living"]

ROOM_FIXTURES={
    "entry": ["ceiling"],
    "hall": ["sconce-n", "sconce-s"],
    "bath": ["ceiling", "mirror", "shower"],
    "bedroom": ["ceiling", "bedside-l", "bedside-r", "reading"],
    "ensuite": ["ceiling", "mirror"],
    "kitchen": ["ceiling", "counter"],
    "living": ["ceiling", "floor-lamp", "accent", "reading"],
}

ROOMS_WITH_WINDOWS={"bedroom", "ensuite", "kitchen", "living"}

room_light_state={
    room: {fx: 0 for fx in fixtures} for room, fixtures in ROOM_FIXTURES.items()
}

selected_room=None
curtain_open=False

def room_is_on(room_id: str) -> bool:
    return any(v>5 for v in room_light_state.get(room_id, {}).values())

def compute_led_states() -> list[str]:
    cmds=[]
    if selected_room and selected_room in ROOM_FIXTURES:
        fixtures=ROOM_FIXTURES[selected_room]
        for i in range(8):
            if i<len(fixtures):
                on=room_light_state[selected_room].get(fixtures[i], 0)>5
            else:
                on=False
            cmds.append(("D", i, on))
    else:
        for i, room_id in enumerate(ROOM_ORDER):
            cmds.append(("D", i, room_is_on(room_id)))
        any_on=any(room_is_on(r) for r in ROOM_ORDER)
        cmds.append(("D", 7, any_on))
    return cmds

_led_state=[None]*8
def sync_leds():
    desired=compute_led_states()
    for kind, idx, on in desired:
        if _led_state[idx]!=on:
            _led_state[idx]=on
            send_serial(f"D{idx}")
            
def sync_leds_full():
    desired=compute_led_states()
    want={idx: on for (_, idx, on) in desired}
    all_on=all(want.get(i, False) for i in range(8))
    all_off=not any(want.get(i, False) for i in range(8))
    if all_on:
        send_serial("H")
        for i in range(8): _led_state[i]=True
        return
    if all_off:
        send_serial("L")
        for i in range(8): _led_state[i]=False
    for idx, on in want.items():
        if _led_state[idx]!=on:
            send_serial(f"D{idx}")
            _led_state[idx]=on
            
_client_queues=[]
_client_lock=threading.Lock()

def broadcast(event: str, data: str):
    msg=f"event: {event}\ndata: {data}\n\n"
    with _client_lock:
        dead=[]
        for q in _client_queues:
            try:
                q.put_nowait(msg)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _client_queues.remove(q)

BUTTON_MAP=[
    (800, 1023, "home"),
    (600, 799, "settings"),
    (430, 599, "volume_up"),
    (270, 429, "volume_down"),
    (150, 269, "power"),
    (50, 149, "call_service"),
]

def map_button(analog_value):
    for lo, hi, name in BUTTON_MAP:
        if lo<=analog_value<=hi:
            return name
    return None

_screen_active=False
PROXIMITY_CM=20
PROXIMITY_MIN=2

def listen_arduino():
    global _screen_active
    log.info("Arduino listener thread started")
    while True:
        if arduino and arduino.is_open:
            try:
                if arduino.in_waiting>0:
                    raw=arduino.readline().decode('utf-8', errors="replace").strip()
                    log.debug(f"<- {raw}")
                    if raw.startswith("DATA|"):
                        parts=raw[5:].split("|")
                        with _lock:
                            for part in parts:
                                if ":" not in part:
                                    continue
                                key, value=part.split(":", 1)
                                key=key.strip()
                                value=value.strip()
                                if key in sensor_data:
                                    sensor_data[key]=value
                        with _lock:
                            d=sensor_data.get("distance", "--")
                        try:
                            dist=int(d)
                            if PROXIMITY_MIN<dist<PROXIMITY_CM:
                                if not _screen_active:
                                    _screen_active=True
                                    broadcast("proximity", "wake")
                                    log.info(f"Wake (distance={dist}cm)")
                            else:
                                if _screen_active:
                                    _screen_active=False
                                    broadcast("proximity", "sleep")
                                    log.info(f"Sleep (distance={dist}cm)")
                        except ValueError:
                            pass
                    elif raw.startswith("EVENT|button:"):
                        try:
                            val=int(raw.split(":", 1)[1])
                            name=map_button(val)
                            if name:
                                broadcast("button", name)
                                log.info(f"Button: {name} (analog={val})")
                        except (ValueError, IndexError):
                            pass
                    elif raw.startswith("ERR|"):
                        log.warning(f"Arduino error: {raw}")
                    elif raw.startswith("STATUS:"):
                        log.info(f"Arduino status: {raw}")
            except Exception as e:
                log.error(f"Serial read error: {e}")
        time.sleep(0.05)
        
@app.route('/')
def serve_index():
    index=DIST_DIR/"index.html"
    if not index.exists():
        return (
            "<h2>UI not built</h2>"
            "<p>Run <code>cd gui-user && npm run build</code> first.</p>",
            404
        )
    return send_from_directory(DIST_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    target=DIST_DIR/path
    if target.exists():
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")

@app.route('/api/dati')
def gather_data():
    with _lock:
        data=dict(sensor_data)
    return jsonify(data)

@app.route('/api/events')
def sse_stream():
    q=queue.Queue(maxsize=32)
    with _client_lock:
        _client_queues.append(q)
    
    def generate():
        yield "retry: 3000\n\n"
        yield f"event: proximity\ndata: {'wake' if _screen_active else 'sleep'}\n\n"
        try:
            while True:
                try:
                    msg=q.get(timeout=20)
                    yield msg
                except queue.Empty:
                    yield "event: heartbeat\ndata: ping\n\n"
        except GeneratorExit:
            with _client_lock:
                try:
                    _client_queues.remove(q)
                except ValueError:
                    pass
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.route("/api/lights", methods=["POST"])
def update_lights():
    global selected_room
    data=request.get_json(force=True)
    room=data.get("room")
    fixtures=data.get("fixtures", {})
    selected_room=data.get("selectedRoom")
    if room and room in room_light_state:
        with _state_lock:
            for fx_id, value in fixtures.items():
                if fx_id in room_light_state[room]:
                    room_light_state[room][fx_id]=int(value)
        sync_leds_full()
        log.info(f"Lights updated - room:{room} selected:{selected_room}")
    return jsonify(status="ok")

@app.route("/api/curtain", methods=["POST"])
def curtain_command():
    global curtain_open
    data=request.get_json(force=True)
    value=int(data.get("value", 50))
    target_open=(value>=50)
    if target_open!=curtain_open:
        cmd="OPEN" if target_open else "CLOSE"
        ok=send_serial(cmd)
        if ok:
            curtain_open=target_open
            log.info(f"Curtain -> {cmd} (value={value})")
            return jsonify(status="ok", action=cmd, open=curtain_open)
        else:
            return jsonify(status="error", msg="Serial unavailable"), 503
    return jsonify(status="ok", action="no-change", open=curtain_open)
   
@app.route("/api/command/<cmd>")
def send_command(cmd):
    ALLOWED={"H", "L", "N", "OPEN", "CLOSE"} | {f"D{i}" for i in range(8)}
    if cmd not in ALLOWED:
        return jsonify(status="error", msg=f"Unknown command: {cmd}"), 400
    if cmd=="H":
        with _state_lock:
            for room in room_light_state:
                for fx in room_light_state[room]:
                    room_light_state[room][fx]=100
        for i in range(8):
            _led_state[i]=True
    elif cmd=="L":
        with _state_lock:
            for room in room_light_state:
                for fx in room_light_state[room]:
                    room_light_state[room][fx]=0
        for i in range(8):
            _led_state[i]=False
    ok=send_serial(cmd)
    if ok:
        return jsonify(status="success", sent=cmd)
    return jsonify(status="error", msg="Serial unavailable"), 503
        
if __name__=="__main__":
    t=threading.Thread(target=listen_arduino, daemon=True)
    t.start()
    log.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)