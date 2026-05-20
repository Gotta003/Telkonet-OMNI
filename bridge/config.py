from pathlib import Path

#Paths
BASE_DIR=Path(__file__).resolve().parent.parent
DIST_DIR=BASE_DIR/"gui-user"/"dist"

#Server
HOST="0.0.0.0"
PORT=5000
DEBUG=False
BRIDGE_URL=f"http://127.0.0.1:{PORT}"

#Arduino
BAUD_RATE=9600
CONNECT_WAIT=2
USER_PORTS={
    "matteo": ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"],
    "mike": ["COM3"],
}

#Proximity Low Power Mode
PROXIMITY_WAKE_CM=20
PROXIMITY_NOISE_CM=2

#Button Mapping
BUTTON_MAP=[
    (800, 1023, "home"),
    (600, 799, "settings"),
    (430, 599, "volume_up"),
    (270, 429, "volume_down"),
    (150, 269, "power"),
    (50, 149, "call_service"),
]

#Rooms
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

#Curtains
CURTAIN_OPEN_THRESHOLD=50

#Commands
ALLOWED_COMMANDS={"H", "L", "N", "OPEN", "CLOSE"} | {f"D{i}" for i in range(8)}