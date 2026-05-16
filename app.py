from flask import Flask, jsonify, send_from_directory, abort
import serial
import threading
import time
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
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
_lock=threading.Lock()
sensor_data={
    "temperature": "--",
    "humidity": "--",
    "light": "--",
    "distance": "--",
}

def listen_arduino():
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
                    elif raw.startswith("EVENT|"):
                        log.info(f"Arduino event: {raw}")
                    elif raw.startswith("ERR|"):
                        log.warning(f"Arduino error: {raw}")
                    elif raw.startswith("STATUS:"):
                        log.info(f"Arduino status: {raw}")
            except Exception as e:
                log.error(f"Serial read error: {e}")
        time.sleep(0.05)
        
@app.route('/')
def dashboard():
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

@app.route("/api/command/<cmd>")
def send_command(cmd):
    ALLOWED={"H", "L", "N", "OPEN", "CLOSE"} | {f"D{i}" for i in range(8)}
    if cmd not in ALLOWED:
        return jsonify(status="error", msg=f"Unknown command: {cmd}"), 400
    if not arduino or not arduino.is_open:
        return jsonify(status="error", msg="Arduino not connected"), 503
    try:
        arduino.write(f"{cmd}\n".encode())
        log.info(f"-> {cmd}")
        return jsonify(status="success", sent=cmd)
    except serial.SerialException as e:
        log.error(f"Serial write error: {e}")
        return jsonify(status="error", msg=str(e)), 500
        
if __name__=="__main__":
    t=threading.Thread(target=listen_arduino, daemon=True)
    t.start()
    log.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)