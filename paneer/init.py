from paneer.serve_gui import start_server
from paneer.proto import paneer_run
import threading
import asyncio

def run_websocket():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()

def run_gtk():
    paneer_run()

def run_app():
    websocket_thread = threading.Thread(target=run_websocket)
    websocket_thread.start()

    run_gtk()

    websocket_thread.join()