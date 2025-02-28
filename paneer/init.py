from paneer.serve_gui import app
from paneer.proto import paneer_run
import threading

def run_flask():
    app.run(port=8765)

def run_gtk():
    paneer_run()

def run_app():
    flask_thread = threading.Thread(target=run_flask)

    flask_thread.start()
    run_gtk()

    flask_thread.join()
