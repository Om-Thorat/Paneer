import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, Gio
from gi.repository import WebKit
import sys
import os
from paneer.comms import exposed_functions
import json
import asyncio
import threading

class Paneer:
    def discover_gui(self):
        if getattr(sys, "frozen", False):
            # Some weird thing when bundled with pyinstaller the bootloader sets path in _MEIPASS
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            application_path = os.path.dirname(application_path)

        directory_to_serve = os.path.join(application_path, "gui")

        return directory_to_serve + "/index.html"
        
    def __init__(self):
        self.app = Gtk.Application(application_id="com.github.om-thorat.Example", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.app.connect("activate", self.on_activate)
        self.app.run()
        
    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_default_size(800, 600)

        self.webview = WebKit.WebView()
        self.webview.get_settings().set_allow_file_access_from_file_urls(True)
        self.webview.get_user_content_manager().register_script_message_handler("paneer")

        self.webview.get_user_content_manager().connect("script-message-received::paneer", self.on_invoke_handler)
        
        dir_to_serve = self.discover_gui()
        self.webview.load_uri("file://" + dir_to_serve)
        self.window.set_child(self.webview)
        self.window.present()

    def on_invoke_handler(self, webview, message):
        def thread_function():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.on_invoke(webview, message))
            loop.close()
            return result

        #  because gtk is not thread safe sooo gotta run in diff thread :(
        #  but this also means we can "run out" of threads so FIXME
        threading.Thread(target=thread_function, daemon=True).start()
            
    async def on_invoke(self, webview, message):
        msg = json.loads(message.to_json(2))
        func = msg["func"]
        args = msg["args"].values()
        print(func, args)
        try:
            if func in exposed_functions:
                result = exposed_functions[func](*args)
                if hasattr(result, '__await__'):
                    result = await result
            else:
                result = f"Function {func} not found"
                
            print(result)
            json_result = json.dumps(result)
            self.webview.evaluate_javascript(f"window.paneer._resolve({json_result});", -1, None, None)
        except Exception as e:
            error_msg = json.dumps(str(e))
            self.webview.evaluate_javascript(f"window.paneer._resolve({{error: {error_msg}}});", -1, None, None)

    def invoke(self, func, args):
        if func in exposed_functions:
            return exposed_functions[func](*args)
        else:
            return f"Function {func} not found"

if __name__ == "__main__":
    Paneer()

# def on_activate(app):
#     webview = WebKit.WebView()
#     context = webview.get_context()
#     print(help(context))
#     webview.load_uri("file://" + discover_gui())
#     win.set_child(webview)
#     win.present()


