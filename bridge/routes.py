import queue
import threading
import logging

from flask import Blueprint, jsonify, send_from_directory, stream_with_context, request, Response
from config import DIST_DIR, ALLOWED_COMMANDS, CURTAIN_OPEN_THRESHOLD
import hardware

log=logging.getLogger(__name__)
bp=Blueprint("omni", __name__)

#SSE Broadcast
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
            
hardware.set_broadcast(broadcast)

@bp.route('/')
def serve_index():
    index=DIST_DIR/"index.html"
    if not index.exists():
        return (
            "<h2>UI not built</h2>"
            "<p>Run <code>cd gui-user && npm run build</code> first.</p>",
            404
        )
    return send_from_directory(DIST_DIR, "index.html")

@bp.route("/<path:path>")
def serve_static(path):
    target=DIST_DIR/path
    if target.exists():
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")

@bp.route('/api/dati')
def gather_data():
    return jsonify(hardware.get_sensor_data())

@bp.route('/api/events')
def sse_stream():
    q=queue.Queue(maxsize=32)
    with _client_lock:
        _client_queues.append(q)
    
    def generate():
        yield "retry: 3000\n\n"
        state="wake" if hardware.is_screen_active() else "sleep"
        yield f"event: proximity\ndata: {state}\n\n"
        try:
            while True:
                try:
                    yield q.get(timeout=20)
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

@bp.route("/api/lights", methods=["POST"])
def update_lights():
    data=request.get_json(force=True)
    room=data.get("room")
    fixtures=data.get("fixtures", {})
    selected=data.get("selectedRoom")
    hardware.set_selected_room(selected)
    if room:
        for fx_id, value in fixtures.items():
            try:
                hardware.update_fixture(room, fx_id, int(value))
            except (ValueError, TypeError):
                pass
        hardware.sync_leds_full()
        log.info(f"Lights - room:{room} selected: {selected}")
    broadcast("lights", f"{room or 'none'}:{selected or 'none'}")
    return jsonify(status="ok")

@bp.route("/api/curtain", methods=["POST"])
def curtain_command():
    data=request.get_json(force=True)
    value=int(data.get("value", 50))
    target_open=(value>=CURTAIN_OPEN_THRESHOLD)
    if target_open!=hardware.get_curtain():
        cmd="OPEN" if target_open else "CLOSE"
        ok=hardware.send_serial(cmd)
        if ok:
            hardware.set_curtain(target_open)
            broadcast("curtain", cmd.lower())
            log.info(f"Curtain -> {cmd}")
            return jsonify(status="ok", action=cmd, open=target_open), 200
        return jsonify(status="error", msg="Serial Unavailable"), 503
    return jsonify(status="ok", action="no-change", open=hardware.get_curtain())
   
@bp.route("/api/command/<cmd>")
def send_command(cmd):
    if cmd not in ALLOWED_COMMANDS:
        return jsonify(status="error", msg=f"Unknown: {cmd}"), 400
    if cmd=="H":
        hardware.set_all_fixtures(100)
        hardware.force_led_state(True)
    elif cmd=="L":
        hardware.set_all_fixtures(0)
        hardware.force_led_state(False)
    ok=hardware.send_serial(cmd)
    if ok:
        broadcast("command", cmd)
        return jsonify(status="success", sent=cmd)
    return jsonify(status="error", msg="Serial unavailable"), 503

@bp.route("/api/state")
def full_state():
    return jsonify({
        "sensors": hardware.get_sensor_data(),
        "lights": hardware.get_room_light_state(),
        "selectedRoom": hardware.get_selected_room(),
        "curtainOpen": hardware.get_curtain(),
        "screenActive": hardware.is_screen_active(),
    })