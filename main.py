from paneer.comms import paneer_command, paneer_command_blocking
from paneer.proto import Paneer
import time

@paneer_command
async def greet():
    app.window.height = 300
    return "hello from py"
 
@paneer_command_blocking
def add(a,b):
    time.sleep(5)
    return (int(a)+int(b))

app = Paneer()
app.window.height = 400
app.window.width = 600
app.window.title = "Paneer"

app.run()