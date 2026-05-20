import threading
import time
import logging
import json
import requests
import sseclient
from constants import BRIDGE_URL

log=logging.getLogger(__name__)
#State Cache
_state_lock=threading.Lock()
_state={
    "sensors": {
        "temperature": "--",    
        "humidity": "--", "light": "--",
        "distance": "--"
    },
    "lights": {},
    "selectedRoom": None,
    "curtainOpen": False,
    "screenActive": False,
    "connected": False,
}

def get_state() -> dict:
    with _state_lock:
        return dict(_state)
    
def _set_state(key, value):
    with _state_lock:
        _state[key]=value
        
_callbacks={
    "state_update": [], #After each /api/state poll
    "proximity": [], #Wake or Sleep
    "button": [], #Button name
    "lights": [], #Any light change
    "curtain": [], #Open or closed call
    "command": [], #command is echo
    "connect": [],  #Success Connection
    "disconnect": [], #Connection Loss
}

def on(event: str, fn):
    if event in _callbacks:
        _callbacks[event].append(fn)
        
def _fire(event: str, data=None):
    for fn in _callbacks.get(event, []):
        try:
            fn(data)
        except Exception as e:
            log.error(f"Callback error [{event}]: {e}")
            
POLL_INTERVAL=2.0

def _poll_loop():
    was_connected=False
    while True:
        if requests is None:
            time.sleep(POLL_INTERVAL)
            continue
        try:
            r=requests.get(f"{BRIDGE_URL}/api/state", timeout=3)
            r.raise_for_status()
            data=r.json()
            with _state_lock:
                _state.update(data)
                _state["connected"]=True
            if not was_connected:
                was_connected=True
                _fire("connect")
                log.info(f"Connected to bridge at {BRIDGE_URL}")
            _fire("state_update", get_state())
        except Exception as e:
            if was_connected:
                was_connected=False
                _set_state("connected", False)
                _fire("disconnect")
                log.warning(f"Bridge unreachable: {e}")
        time.sleep(POLL_INTERVAL)
        
def _sse_loop():
    if requests is None or sseclient is None:
        log.warning("requests/sseclient not installed - SSE disabled")
        return
    while True:
        try:
            response=requests.get(
                f"{BRIDGE_URL}/api/events",
                stream=True,
                timeout=60,
                headers={"Accept": "text/event-stream"},
            )
            client=sseclient.SSEClient(response)
            log.info("SSE stream connected")
            for event in client.events():
                if event.event=="proximity":
                    _set_state("screenActive", event.data=="wake")
                    _fire("proximity", event.data)
                elif event.event=="button":
                    _fire("button", event.data)
                elif event.event=="lights":
                    _fire("lights", event.data)
                elif event.event=="curtain":
                    open_=event.data=="open"
                    _set_state("curtainOpen", open_)
                    _fire("curtain", event.data)
                elif event.event=="command":
                    _fire("command", event.data)
        except Exception as e:
            log.warning(f"SSE disconnected: {e} - retrying in 3 seconds")
            time.sleep(3)
            
def send_command(cmd: str) -> bool:
    if requests is None:
        return False
    try:
        r=requests.get(f"{BRIDGE_URL}/api/command/{cmd}", timeout=3)
        return r.ok
    except Exception as e:
        log.error(f"Command error: {e}")
        return False
    
def set_light(room: str, fixture: str, value: int, selected_room: str=None) -> bool:
    if requests is None:
        return False
    try:
        r=requests.post(
            f"{BRIDGE_URL}/api/lights",
            json={"room": room, "fixtures": {fixture: value}, "selectedRoom": selected_room},
            timeout=3
        )
        return r.ok
    except Exception as e:
        log.error(f"Light error: {e}")
        return False
    
def set_curtain(value: int)->bool:
    if requests is None:
        return False
    try:
        r=requests.post(f"{BRIDGE_URL}/api/curtain", json={"value": value}, timeout=3)
        return r.ok
    except Exception as e:
        log.error(f"Curtain error: {e}")
        return False

def start():
    threading.Thread(target=_poll_loop, daemon=True).start()
    threading.Thread(target=_sse_loop, daemon=True).start()
    log.info(f"Network client started -> {BRIDGE_URL}")    