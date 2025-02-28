import functools

exposed_functions = {}

def paneer_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    exposed_functions[func.__name__] = func
    return wrapper

