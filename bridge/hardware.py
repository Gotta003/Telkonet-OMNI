import serial
import threading
import time
import logging
from config import USER_PORTS, BAUD_RATE, CONNECT_WAIT, ROOM_ORDER, ROOM_FIXTURES, PROXIMITY_NOISE_CM, PROXIMITY_WAKE_CM, BUTTON_MAP

log=logging.getLogger(__name__)
_arduino=None
_serial_lock=threading.Lock()

def connect_arduino():
    global _arduino
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

def send_serial(cmd: str):
    if not _arduino or not _arduino.is_open:
        log.warning(f"Serial unavailable - dropped: {cmd}")
        return False
    try:
        with _serial_lock:
            _arduino.write(f"{cmd}\n".encode())
        log.info(f"-> {cmd}")
        return True
    except serial.SerialException as e:
        log.error(f"Serial write error: {e}")
        return False
    
def get_arduino():
    return _arduino

#SENSORS
_sensor_lock=threading.Lock
_sensor_data={
    "temperature": "--",
    "humidity": "--",
    "light": "--",
    "distance": "--",
}

def get_sensor_data() -> dict:
    with _sensor_lock:
        return dict(_sensor_data)
    
def _update_sensor(key: str, value: str):
    with _sensor_lock:
        if key in _sensor_data:
            _sensor_data[key]=value
            
#LED
_led_lock=threading.Lock()
_led_state=[None]*8
_room_lock=threading.Lock()
_selected_room=None
_curtain_open=False

_room_light_state={
    room: {fx: 0 for fx in fixtures} for room, fixtures in ROOM_FIXTURES.items()
}

def set_selected_room(room_id):
    global _selected_room
    with _room_lock:
        _selected_room=room_id

def get_selected_room():
    with _room_lock:
        return _selected_room
    
def set_curtain(open_: bool):
    global _curtain_open
    _curtain_open=open_
    
def get_curtain():
    return _curtain_open

def update_fixture(room_id: str, fx_id: str, value: int):
    with _room_lock:
        if room_id in _room_light_state and fx_id in _room_light_state[room_id]:
            _room_light_state[room_id][fx_id]=value
            
def get_room_light_state():
    with _room_lock:
        return {r: dict(fx) for r, fx in _room_light_state.items()}
    
def set_all_fixtures(value: int):
    with _room_lock:
        for room in _room_light_state:
            for fx in _room_light_state[room]:
                _room_light_state[room][fx]=value
                
def room_is_on(room_id: str) -> bool:
    with _room_lock:
        return any(v>5 for v in _room_light_state.get(room_id, {}).values())
    
def _compute_led_targets() -> dict:
    sel=get_selected_room()
    targets={}
    if sel and sel in ROOM_FIXTURES:
        fixtures=ROOM_FIXTURES[sel]
        for i in range(8):
            if i<len(fixtures):
                with _room_lock:
                    targets[i]=_room_light_state[sel].get(fixtures[i], 0)>5
            else:
                targets[i]=False
    else:
        for i, room_id in enumerate(ROOM_ORDER):
            targets[i]=room_is_on(room_id)
        targets[7]=any(room_is_on(r) for r in ROOM_ORDER)
    return targets

def sync_leds_full():
    targets=_compute_led_targets()
    all_on=all(targets.get(i, False) for i in range(8))
    all_off=not any(targets.get(i, False) for i in range(8))
    with _led_lock:
        if all_on:
            send_serial("H")
            for i in range(8): _led_state[i]=True
            return
        if all_off:
            send_serial("L")
            for i in range(8): _led_state[i]=False
        for idx, on in targets.items():
            if _led_state[idx]!=on:
                send_serial(f"D{idx}")
                _led_state[idx]=on
                
def force_led_state(all_on: bool):
    with _led_lock:
        for i in range(8):
            _led_state[i]=all_on
            
def map_button(analog_value: int):
    for lo, hi, name in BUTTON_MAP:
        if lo<=analog_value<=hi:
            return name
    return None

#Arduino listener thread
_screen_active=False
_broadcast_fn=None

def set_broadcast(fn):
    global _broadcast_fn
    _broadcast_fn=fn
    
def _broadcast(event: str, data: str):
    if _broadcast_fn:
        _broadcast_fn(event, data)
        
def start_listener():
    t=threading.Thread(target=_listen_loop, daemon=True)
    t.start()
    log.info("Arduino Listener Started")
    
def _listen_loop():
    global _screen_active
    while True:
        arduino=get_arduino()
        if arduino and arduino.is_open:
            try:
                if arduino.in_waiting>0:
                    raw=arduino.readline().decode("utf-8", errors="replace").strip()
                    log.debug(f"<- {raw}")
                    _handle_line(raw)
            except Exception as e:
                log.error(f"Serial read error: {e}")
        time.sleep(0.05)
    
def _handle_line(raw: str):
    global _screen_active
    if raw.startswith("DATA|"):
        parts=raw[5:].split("|")
        for part in parts:
            if ":" not in part:
                continue
            key, value=part.split(":", 1)
            _update_sensor(key.strip(), value.strip())
        
        dist_raw=_sensor_data.get("distance", "--")
        try:
            dist=int(dist_raw)
            if PROXIMITY_NOISE_CM<dist<PROXIMITY_WAKE_CM:
                if not _screen_active:
                    _screen_active=True
                    _broadcast("proximity", "wake")
                    log.info(f"Wake (distance={dist}cm)")
                else:
                    if _screen_active:
                        _screen_active=False
                        _broadcast("proximity", "sleep")
                        log.info(f"Sleep (Distance={dist}cm)")
                    else:
                        if _screen_active:
                            _screen_active=False
                            _broadcast("proximity", "sleep")
                            log.info(f"Sleep (distance={dist}cm)")
        except ValueError:
            pass
    elif raw.startswith("EVENT|button:"):
        try:
            val=int(raw.split(":", 1)[1])
            name=map_button(val)
            if name:
                _broadcast("button", name)
                log.info(f"Button: {name} (analog={val})")
        except (ValueError, IndexError):
            pass
    elif raw.startswith("ERR|"):
        log.warning(f"Arduino: {raw}")
    elif raw.startswith("STATUS:"):
        log.info(f"Arduino: {raw}")

def is_screen_active() -> bool:
    return _screen_active