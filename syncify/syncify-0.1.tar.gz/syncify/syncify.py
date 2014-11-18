from threading import Event
from functools import partial

def syncify(func, kw='callback'):
    def wrap(func, *args, **kwargs):
        event = Event()
        results = []

        def async(*args):
            # print 'called back'
            # print args
            results.append(args)
            event.set()

        # print 'calling'
        kwargs[kw] = async
        func(*args, **kwargs)
        event.wait()

        # print 'results'
        if len(results) == 1:
            result = results[0]
            length = len(result)
            if length == 0:
                return
            elif length == 1:
                return result[0]
            else:
                return result
        else:
            return

    return partial(wrap,func)
