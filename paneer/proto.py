import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, Gio, GLib
from gi.repository import WebKit
import sys
import os
from paneer.comms import exposed_functions
import json
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import importlib.resources as resources

currEnv = os.getenv("paneer_env")

paneer_init_js = ""
with resources.files("paneer").joinpath("paneer.js").open("r", encoding="utf-8") as f:
    paneer_init_js = f.read()

class Window:
    def __init__(self,app, title="Paneer", width=800, height=600):
        self._app = app
        self.title = title
        self.width = width
        self.height = height
        self.resizable = True
    
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value: str):
        self._title = value
        if self._app and self._app.app_window:
            self._app.app_window.set_title(self._title)

    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value: int):
        if (value <= 0):
            raise ValueError("Height must be a positive integer")
        self._height = value
        if self._app and self._app.app_window:
            self._app.app_window.set_default_size(self._width, self._height)

    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value: int):
        if (value <= 0):
            raise ValueError("Width must be a positive integer")
        self._width = value
        if self._app and self._app.app_window:
            self._app.app_window.set_default_size(self._width, self._height)
        
class Paneer:
    def discover_ui(self):
        cwd = os.getcwd()
        cwd_dist = os.path.join(cwd, "dist")
        if os.path.isdir(cwd_dist):
            directory_to_serve = cwd_dist
        
        if getattr(sys, "frozen", False):
            # Some weird thing when bundled with pyinstaller the bootloader sets path in _MEIPASS
            application_path = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
            dist_path = os.path.join(application_path, "dist")
            if os.path.isdir(dist_path):
                directory_to_serve = dist_path

        return directory_to_serve + "/index.html"
        
    def __init__(self):
        self.app = Gtk.Application(application_id="com.github.om-thorat.Example", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.app.connect("activate", self.on_activate)
        self.app_window = None
        self.window = Window(self)
        self.task_loop = asyncio.new_event_loop()
        self.task_thread = threading.Thread(target=self.task_loop.run_forever, daemon=True)
        self.task_thread.start()

        self.executor = ThreadPoolExecutor(max_workers=8)

    def on_activate(self, app):
        self.app_window = Gtk.ApplicationWindow(application=app)
        self.app_window.set_title(self.window.title)
        self.app_window.set_default_size(self.window.width, self.window.height)
        self.app_window.set_resizable(self.window.resizable)


        self.manager = WebKit.UserContentManager()
        self.manager.add_script(WebKit.UserScript(
            paneer_init_js,
            WebKit.UserContentInjectedFrames.ALL_FRAMES,
            WebKit.UserScriptInjectionTime.END,
        ))

        self.webview = WebKit.WebView(user_content_manager=self.manager)
        self.webview.get_settings().set_allow_file_access_from_file_urls(True)
        self.webview.get_user_content_manager().register_script_message_handler("paneer")
        self.webview.get_user_content_manager().connect("script-message-received::paneer", self.on_invoke)

        
        self.webview.get_settings().set_enable_developer_extras(True)
        if(currEnv == "dev"):
            self.webview.load_uri("http://localhost:5173")
        else:
            dir_to_serve = self.discover_ui()
            self.webview.load_uri("file://" + dir_to_serve)
        self.app_window.set_child(self.webview)
        self.app_window.present()

    def run(self):
        self.app.run()

    def _return_result(self, result, msg_id):
            def send():
                json_result = json.dumps({"result": result, "id": msg_id})
                self.webview.evaluate_javascript(f"window.paneer._resolve({json_result});", -1, None, None)
            GLib.idle_add(send)

    def on_invoke(self, webview, message):
        msg = json.loads(message.to_json(2))
        func = msg["func"]
        func_info = exposed_functions.get(func)

        if not func_info:
            error_msg = json.dumps({"error": f"Function {func} not found", "id": msg["id"]})
            self.webview.evaluate_javascript(f"window.paneer._resolve({error_msg});", -1, None, None)
            return

        blocking = func_info and func_info.get("blocking", False)
        func = func_info["function"] if func_info else None

        if blocking:
            future = self.executor.submit(func, *msg["args"].values())
            future.add_done_callback(lambda f: self._return_result(f.result(), msg["id"]))
        elif asyncio.iscoroutinefunction(func_info["function"]):
            future = asyncio.run_coroutine_threadsafe(func(*msg["args"].values()), self.task_loop)
            future.add_done_callback(lambda f: self._return_result(f.result(), msg["id"]))
        else:
            res = func(*msg["args"].values())
            self._return_result(res, msg["id"])

    def invoke(self, func, args):
        if func in exposed_functions:
            return exposed_functions[func](*args)
        else:
            return f"Function {func} not found"

if __name__ == "__main__":
    Paneer()



 