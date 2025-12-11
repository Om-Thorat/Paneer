import json
import os
import sys
import importlib.resources as resources
from paneer.base import PaneerBase, WindowBase

# needs pythonnet, Microsoft.Web.WebView2.WinForms.dll, Microsoft.Web.WebView2.Core.dll

try:
    import clr
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Threading")
    clr.AddReference("System.Drawing")
    
    try:
        clr.AddReference("Microsoft.Web.WebView2.WinForms")
        clr.AddReference("Microsoft.Web.WebView2.Core")
    except Exception:
        print("Warning: Microsoft.Web.WebView2 DLLs not found.")

    from System.Windows.Forms import Application, Form, DockStyle, Control
    from System.Drawing import Size
    from Microsoft.Web.WebView2.WinForms import WebView2
    from Microsoft.Web.WebView2.Core import CoreWebView2HostResourceAccessKind
except ImportError:
    if sys.platform == "win32":
        print("Error: pythonnet not installed or DLLs missing.")
    pass

currEnv = os.getenv("paneer_env")

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
        
        self.form = Form()
        self.form.Text = self.window.title
        self.form.Size = Size(self.window.width, self.window.height)
        
        self.webview = WebView2()
        self.webview.Dock = DockStyle.Fill
        self.form.Controls.Add(self.webview)
        
        self.form.Load += self.on_form_load

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
            core_webview.Navigate("http://localhost:5173")
        else:
            folder_path = self.discover_ui()
            core_webview.SetVirtualHostNameToFolderMapping(
                "paneer.local", 
                folder_path, 
                CoreWebView2HostResourceAccessKind.Allow
            )
            core_webview.Navigate("https://paneer.local/index.html")

    def run(self):
        Application.Run(self.form)

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
