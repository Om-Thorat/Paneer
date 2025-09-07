from paneer.comms import paneer_command, paneer_command_blocking
from paneer.proto import Paneer, Window
import time

@paneer_command
async def greet():
    app.window_props.height = 300
    return "hello from py"
 
@paneer_command_blocking
def add(a,b):
    time.sleep(5)
    return (int(a)+int(b))

win = Window()
win.height = 500
win.width = 500
win.resizable = False
win.title = "Paneer"

app = Paneer(win)

app.run()