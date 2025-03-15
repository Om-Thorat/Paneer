from paneer.comms import paneer_command
from paneer.proto import Paneer
import time

@paneer_command
async def greet():
    return "hello from py"
 
@paneer_command
async def add(a,b):
    time.sleep(3)
    return (int(a)+int(b))

Paneer()