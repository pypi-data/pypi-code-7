from decorator import decorator
from gevent.lock import RLock

# A global lock to control configuration management.
global_config_lock = RLock()


@decorator
def config_lock(func, *args, **kwargs):
    with global_config_lock:
        return func(*args, **kwargs)
