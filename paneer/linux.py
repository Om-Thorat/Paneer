import gi
gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, Gio, GLib, WebKit
import sys
import os
import json
import importlib.resources as resources
from paneer.base import PaneerBase, WindowBase

currEnv = os.getenv("paneer_env")

paneer_init_js = ""
with resources.files("paneer").joinpath("paneer.js").open("r", encoding="utf-8") as f:
    paneer_init_js = f.read()

class Window(WindowBase):
    def update_title(self):
        if self._app.app_window:
            self._app.app_window.set_title(self._title)

    def update_size(self):
        if self._app.app_window:
            self._app.app_window.set_default_size(self._width, self._height)

class Paneer(PaneerBase):
    def create_window(self):
        return Window(self)

    def __init__(self):
        super().__init__()
        
        self.app = Gtk.Application(application_id="com.github.om-thorat.Example", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.app.connect("activate", self.on_activate)
        self.app_window = None

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
        self.webview.get_user_content_manager().connect("script-message-received::paneer", self.on_invoke_handler)
        
        self.webview.get_settings().set_enable_developer_extras(True)
        
        if currEnv == "dev":
            self.webview.load_uri("http://localhost:5173")
        else:
            dir_to_serve = self.discover_ui()
            self.webview.load_uri("file://" + dir_to_serve + "/index.html")
            
        self.app_window.set_child(self.webview)
        self.app_window.present()

    def run(self):
        self.app.run()

    def _execute_js(self, script):
        def run_on_main():
            self.webview.evaluate_javascript(script, -1, None, None)
        GLib.idle_add(run_on_main)

    def on_invoke_handler(self, webview, message):
        try:
            msg = json.loads(message.to_json(2))
            self.handle_rpc(msg)
        except Exception as e:
            print(f"Error parsing RPC message: {e}")
