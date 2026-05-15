from flask import Flask, render_template_string, jsonify, Response
import serial
import threading
import time
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent
LOG_FILE=BASE_DIR/"arduino_thread.log"
html_path=BASE_DIR/"gui-user/dist/index.html"

def load_ui():
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()
    
HTML_UI=load_ui()
print("Loaded Interface")

app=Flask(__name__)
user_ports={
    "matteo": ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"],
    "mike": ["COM3"],
}
def connect_arduino():
    for user, ports in user_ports.items():
        for port in ports:
            try:
                # Try connection
                conn = serial.Serial(port=port, baudrate=9600, timeout=1)
                with open(LOG_FILE, "w") as f:
                    f.write(f"Connected to {user}'s port: {port}\n")
                time.sleep(2) 
                return conn
            except (serial.SerialException, OSError):
                continue
    return None
arduino=connect_arduino()
sensor_data={
    "temperature": "--",
    "humidity": "--",
    "light": "--"
}

def listen_arduino():
    global sensor_data
    with open(LOG_FILE, "w") as f:
        f.write("--- Thread Started ---\n")
    while True:
        if arduino and arduino.is_open:
            try:
                if arduino.in_waiting>0:
                    line=arduino.readline().decode('utf-8').strip()
                    with open(LOG_FILE, "a") as f:
                        f.write(f"{time.strftime('%H:%M:%S')} - {line}\n")
                    if "|" in line:
                        parts=line.split("|")
                        for part in parts:
                            if ":" not in part:
                                continue
                            key, value=part.split(":", 1)
                            key=key.strip()
                            value=value.strip()
                            if "Temperature" in key: 
                                sensor_data["temperature"]=value.replace("°C", "").strip()
                            if "Humidity" in key:
                                sensor_data["humidity"]=value.replace("%", "").strip()
                            if key=="Light":
                                sensor_data["light"]=value.strip()
            except Exception as e:
                with open(LOG_FILE, "a") as f:
                    f.write(f"{time.strftime('%H:%M:%S')} ERROR: {e}\n")
        time.sleep(0.5)
        
@app.route('/')
def dashboard():
    content=load_ui()
    return Response(content, mimetype='text/html')

@app.route("/comando/<cmd>")
def send_command(cmd):
    if arduino and arduino.is_open:
        try:
            arduino.write(f"{cmd}\n".encode())
            return jsonify(status="success", sent=cmd)
        except serial.SerialException as e:
            return jsonify(status="error", msg=str(e)), 500
    return jsonify(status="error", msg="Arduino not connected"), 50

@app.route('/api/dati')
def gather_data():
    return jsonify(sensor_data)
        
if __name__=="__main__":
    t=threading.Thread(target=listen_arduino, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=False)