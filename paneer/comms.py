import functools

exposed_functions = {}

def paneer_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    exposed_functions[func.__name__] = {"function": func, "blocking": False}
    return wrapper

def paneer_command_blocking(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    exposed_functions[func.__name__] = {"function": func, "blocking": True}
    return wrapper