import json
import os
import sys
import time
import urllib.request
import threading
import importlib.resources as resources
from paneer.base import PaneerBase, WindowBase

# needs pythonnet, Microsoft.Web.WebView2.WinForms.dll, Microsoft.Web.WebView2.Core.dll

# Add libs to PATH for WebView2Loader.dll
libs_dir = os.path.join(os.path.dirname(__file__), "libs")
if os.path.exists(libs_dir):
    os.environ["Path"] += ";" + libs_dir

try:
    import clr
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Threading")
    clr.AddReference("System.Drawing")
    
    try:
        clr.AddReference(os.path.join(libs_dir, "Microsoft.Web.WebView2.WinForms.dll"))
        clr.AddReference(os.path.join(libs_dir, "Microsoft.Web.WebView2.Core.dll"))
    except Exception:
        try:
            clr.AddReference("Microsoft.Web.WebView2.WinForms")
            clr.AddReference("Microsoft.Web.WebView2.Core")
        except Exception:
            print("Warning: Microsoft.Web.WebView2 DLLs not found.")

    from System.Windows.Forms import Application, Form, DockStyle, Control
    from System.Drawing import Size
    from System import Action
    from System.Threading import Thread, ApartmentState, ThreadStart
    from Microsoft.Web.WebView2.WinForms import WebView2
    from Microsoft.Web.WebView2.Core import CoreWebView2HostResourceAccessKind
except ImportError:
    if sys.platform == "win32":
        print("Error: pythonnet not installed or DLLs missing.")
    pass

currEnv = os.getenv("paneer_env")
print(f"Paneer Environment: {currEnv}")

paneer_init_js = ""
try:
    with resources.files("paneer").joinpath("paneer.js").open("r", encoding="utf-8") as f:
        paneer_init_js = f.read()
except Exception:
    pass

class Window(WindowBase):
    def update_title(self):
        if self._app and hasattr(self._app, 'form') and self._app.form:
            def update():
                self._app.form.Text = self._title
            if self._app.form.InvokeRequired:
                self._app.form.Invoke(update)
            else:
                update()

    def update_size(self):
        if self._app and hasattr(self._app, 'form') and self._app.form:
            def update():
                self._app.form.Size = Size(self._width, self._height)
            if self._app.form.InvokeRequired:
                self._app.form.Invoke(update)
            else:
                update()

class Paneer(PaneerBase):
    def create_window(self):
        return Window(self)

    def __init__(self):
        super().__init__()
        self.form = None
        self.webview = None

    def _init_ui(self):
        self.form = Form()
        self.form.Text = self.window.title
        self.form.Size = Size(self.window.width, self.window.height)
        
        self.webview = WebView2()
        self.webview.Dock = DockStyle.Fill
        self.form.Controls.Add(self.webview)
        
        self.form.Load += self.on_form_load
        Application.Run(self.form)

    def run(self):
        t = Thread(ThreadStart(self._init_ui))
        t.SetApartmentState(ApartmentState.STA)
        t.Start()
        t.Join()

    def on_form_load(self, sender, e):
        try:
            self.webview.EnsureCoreWebView2Async(None)
            self.webview.CoreWebView2InitializationCompleted += self.on_webview_ready
        except Exception as ex:
            print(f"Error initializing WebView2: {ex}")

    def on_webview_ready(self, sender, e):
        if not e.IsSuccess:
            print(f"WebView2 initialization failed: {e.InitializationException}")
            return

        core_webview = self.webview.CoreWebView2
        core_webview.AddScriptToExecuteOnDocumentCreatedAsync(paneer_init_js)
        core_webview.WebMessageReceived += self.on_web_message_received
        core_webview.Settings.AreDevToolsEnabled = True
        
        if currEnv == "dev":
            def wait_and_nav():
                try:
                    url = "http://127.0.0.1:5173"
                    print(f"Waiting for {url}...")
                    
                    # Disable proxies for localhost check
                    proxy_handler = urllib.request.ProxyHandler({})
                    opener = urllib.request.build_opener(proxy_handler)
                    
                    for i in range(60):
                        try:
                            with opener.open(url) as response:
                                if response.status == 200:
                                    print(f"Server ready at {url}")
                                    break
                        except Exception:
                            if i % 10 == 0:
                                print(f"Waiting for frontend... ({i})")
                            time.sleep(0.5)
                    else:
                        print("Timeout waiting for frontend server.")
                        return
                    
                    def nav():
                        print(f"Navigating to {url}")
                        core_webview.Navigate(url)
                    
                    if self.form.InvokeRequired:
                        self.form.Invoke(Action(nav))
                    else:
                        nav()
                except Exception as e:
                    print(f"Error in navigation thread: {e}")

            threading.Thread(target=wait_and_nav, daemon=True).start()
        else:
            folder_path = self.discover_ui()
            file_path = os.path.join(folder_path, "index.html")
            file_url = f"file:///{file_path.replace(os.sep, '/')}"
            print(f"Navigating to {file_url}")
            core_webview.Navigate(file_url)

    def _execute_js(self, script):
        def run_on_main():
            try:
                self.webview.ExecuteScriptAsync(script)
            except Exception as e:
                print(f"Error executing JS: {e}")

        if self.form.InvokeRequired:
            self.form.Invoke(run_on_main)
        else:
            run_on_main()

    def on_web_message_received(self, sender, args):
        try:
            message = args.TryGetWebMessageAsString()
            msg = json.loads(message)
            self.handle_rpc(msg)
        except Exception as e:
            print(f"Error handling web message: {e}")
