from abc import ABC, abstractmethod
import os
import sys
import json
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from paneer.comms import exposed_functions

class WindowBase(ABC):
    def __init__(self, app, title="Paneer", width=800, height=600):
        self._app = app
        self._title = title
        self._width = width
        self._height = height
        self.resizable = True

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self.update_title()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        if value <= 0:
            raise ValueError("Width must be a positive integer")
        self._width = value
        self.update_size()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        if value <= 0:
            raise ValueError("Height must be a positive integer")
        self._height = value
        self.update_size()

    @abstractmethod
    def update_title(self):
        pass

    @abstractmethod
    def update_size(self):
        pass


class PaneerBase(ABC):
    def __init__(self):
        self.task_loop = asyncio.new_event_loop()
        self.task_thread = threading.Thread(target=self.task_loop.run_forever, daemon=True)
        self.task_thread.start()
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.window = self.create_window()

    @abstractmethod
    def create_window(self):
        pass

    def discover_ui(self):
        cwd = os.getcwd()
        cwd_dist = os.path.join(cwd, "dist")
        directory_to_serve = cwd_dist if os.path.isdir(cwd_dist) else cwd
        
        if getattr(sys, "frozen", False):
            application_path = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
            dist_path = os.path.join(application_path, "dist")
            if os.path.isdir(dist_path):
                directory_to_serve = dist_path

        return directory_to_serve

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _execute_js(self, script):
        pass

    def _return_result(self, result, msg_id):
        try:
            json_result = json.dumps({"result": result, "id": msg_id})
            self._execute_js(f"window.paneer._resolve({json_result});")
        except Exception as e:
            self._return_error(str(e), msg_id)

    def _return_error(self, error_msg, msg_id):
        try:
            json_error = json.dumps({"error": error_msg, "id": msg_id})
            self._execute_js(f"window.paneer._resolve({json_error});")
        except Exception:
            print(f"Failed to send error to WebView: {error_msg}")

    def handle_rpc(self, msg):
        """
        msg should be a dict: {"func": str, "args": dict, "id": str}
        """
        func_name = msg.get("func")
        msg_id = msg.get("id")
        
        func_info = exposed_functions.get(func_name)

        if not func_info:
            self._return_error(f"Function {func_name} not found", msg_id)
            return

        blocking = func_info.get("blocking", False)
        func = func_info["function"]
        
        args_dict = msg.values()
        args = args_dict.values() if isinstance(args_dict, dict) else []

        try:
            if blocking:
                future = self.executor.submit(func, *args)
                future.add_done_callback(lambda f: self._handle_future_result(f, msg_id))
            elif asyncio.iscoroutinefunction(func):
                future = asyncio.run_coroutine_threadsafe(func(*args), self.task_loop)
                future.add_done_callback(lambda f: self._handle_future_result(f, msg_id))
            else:
                res = func(*args)
                self._return_result(res, msg_id)
        except Exception as e:
            self._return_error(str(e), msg_id)

    def _handle_future_result(self, future, msg_id):
        try:
            res = future.result()
            self._return_result(res, msg_id)
        except Exception as e:
            self._return_error(str(e), msg_id)

    def invoke(self, func, args):
        if func in exposed_functions:
            return exposed_functions[func](*args)
        else:
            return f"Function {func} not found"
