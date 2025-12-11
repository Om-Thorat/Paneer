import sys

if sys.platform == "linux":
    from paneer.linux import Paneer
elif sys.platform == "win32":
    try:
        from paneer.windows import Paneer
    except ImportError:
        raise NotImplementedError("Windows support is not yet implemented. Please implement paneer/windows.py")
else:
    raise NotImplementedError(f"Platform {sys.platform} is not supported")
