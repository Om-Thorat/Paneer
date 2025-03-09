from paneer.init import run_app
from paneer.comms import paneer_command
import time

@paneer_command
def greet():
    return "hello from py"
 
@paneer_command
def add(a,b):
    time.sleep(10)
    return (int(a)+int(b))

run_app()