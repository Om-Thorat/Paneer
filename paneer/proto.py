import gi

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk
from gi.repository import WebKit
import sys
import os


def discover_gui():
    if getattr(sys, "frozen", False):
        # Some weird thing when bundled with pyinstaller the bootloader sets path in _MEIPASS
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
        application_path = os.path.dirname(application_path)

    directory_to_serve = os.path.join(application_path, "gui")

    return directory_to_serve + "/index.html"


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    webview = WebKit.WebView()
    webview.load_uri("file://" + discover_gui())
    win.set_child(webview)
    win.present()


def paneer_run():
    app = Gtk.Application(application_id="com.github.om-thorat.Example")
    app.connect("activate", on_activate)
    app.run(None)
