"""
Third party profiling decorators.
"""
__all__ = ['timecall', 'coverage', 'memory_profile', 'line_profile']

from functools import wraps

try:
    from memory_profiler import profile as memory_profile
except ImportError:
    pass

try:
    from line_profiler import LineProfiler

    def line_profile(func):
        p = LineProfiler()
        f = p(func)

        def wrapper(*args, **argd):
            try:
                return f(*args, **argd)
            finally:
                p.print_stats()
        return wrapper
except ImportError:
    pass

try:
    from profilehooks import profile as _profile

    def profile(f, immediate=True):
        return _profile(f, immediate=immediate)

except ImportError:
    raise
    try:
        from pstats import Stats

        try:
            from cProfile import Profile
        except ImportError:
            from profile import Profile

        def profile(f, immediate=True):
            @wraps(f)
            def wrapper(*args, **argd):
                profiler = Profile()
                try:
                    profiler.enable()
                    return f(*args, **argd)
                finally:
                    profiler.disable()
                    stats = Stats(profiler)
                    stats.strip_dirs()
                    stats.sort_stats('cumulative')
                    stats.print_stats(f.__name__)
            return wrapper
    except ImportError:
        pass

try:
    from profilehooks import timecall
except ImportError:
    from time import time

    def timecall(f, immediate=True):
        @wraps(f)
        def wrapper(*args, **argd):
            try:
                start = time()
                return f(*args, **argd)
            finally:
                print "\n  %s (%s:%d):\n    %.3f seconds\n" % (
                    f.func_name, f.func_code.co_filename,
                    f.func_code.co_firstlineno,
                    time() - start)
        return wrapper

try:
    from profilehooks import coverage
except ImportError:
    pass
