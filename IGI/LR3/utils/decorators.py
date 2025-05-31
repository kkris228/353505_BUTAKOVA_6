import time
from functools import wraps

def log_execution(func):
    """
    Decorator that logs the execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Running {func.__name__}...")
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[LOG] Done in {time.time() - start:.5f} seconds.")
        return result
    return wrapper