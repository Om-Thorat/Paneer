import gi
gi.require_version("Gtk", "4.0")
gi.require_version('WebKit','6.0')
from gi.repository import Gtk
from gi.repository import WebKit

def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    webview = WebKit.WebView()
    webview.load_uri("http://localhost:8765")
    win.set_child(webview)
    win.present()

def paneer_run():
    app = Gtk.Application(application_id= 'com.github.om-thorat.Example')
    app.connect('activate', on_activate)
    app.run(None)
