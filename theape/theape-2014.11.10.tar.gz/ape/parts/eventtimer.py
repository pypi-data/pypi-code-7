
IN_PWEAVE = __name__ == "__builtin__"


# python standard library
import threading

# this package
from ape import BaseClass
from ape.infrastructure.code_graphs import  module_diagram, class_diagram


class EventTimer(BaseClass):
    """
    A timer object to set an event
    """
    def __init__(self, seconds=0.5, event=None):
        """
        EventTimer constructor

        :param:

         - `event`: a threading.Event to set
         - `seconds`: number of seconds to run the timer
        """
        self._event = event
        self.seconds = seconds
        self._timer = None
        return

    @property
    def event(self):
        """
        Threading event for the timer to set
        """
        if self._event is None:
            self._event = threading.Event()
            # I don't know about this, but I think
            # I want it to always rely on the timer to clear it
            self._event.set()
        return self._event

    @property
    def timer(self):
        """
        A threading.Timer object
        """
        # Timers can only be started once, so this can't be persistent
        return threading.Timer(self.seconds, self.set_event)

    def set_event(self):
        """
        Sets the event
        """
        self.event.set()
        return

    def start(self):
        """
        The main interface - clears the event then starts the timer
        """
        self.event.clear()
        self.timer.start()
        return

    def clear(self):
        """
        A convenience method for users to call the event.clear method.        
        """
        self.event.clear()
        return

    def wait(self, timeout=None):
        """
        Calls event.wait if timeout is None, uses self.seconds
        """
        if timeout is None:
            timeout = self.seconds
        self.event.wait(timeout)
        return

    def close(self):
        """
        Cancels the timer and sets the event.
        """
        self.timer.cancel()
        self.event.set()
        return

    def is_set(self):
        """
        :return: True if self.event is set
        """
        return self.event.is_set()
# end class EventTimer        


if IN_PWEAVE:
    import os
    this_file = os.path.join(os.getcwd(), 'eventtimer.py')
    class_diagram_file = class_diagram(class_name="EventTimer",
                                       filter='OTHER',
                                       module=this_file)
    print ".. image:: {0}".format(class_diagram_file)


def wait(method):
    """
    Decorator to wait for previous timers and to start a new one on exit

    :param:

     - `method`: method to wrap with a timer.wait call

    :return: wrapped method
    """
    def _method(self, *args, **kwargs):
        # wait if timer is running but only up until the time-limit
        self.timer.wait(self.timer.seconds)
        self.timer.clear()
        outcome = method(self, *args, **kwargs)
        self.timer.start()
        return outcome
    return _method                


if IN_PWEAVE:
    module_diagram_file = module_diagram(module=this_file, project='eventtimer')
    print ".. image:: {0}".format(module_diagram_file)
