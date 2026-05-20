import logging
from flask import Flask
from config import HOST, PORT, DEBUG, DIST_DIR
import hardware
import routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

app=Flask(__name__, static_folder=str(DIST_DIR), static_url_path='/assets')
app.register_blueprint(routes.bp)

if __name__=="__main__":
    hardware.connect_arduino()
    hardware.start_listener()
    logging.getLogger(__name__).info(
        f"OMNI BRIDGE -> http://{HOST}:{PORT}"
    )
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)