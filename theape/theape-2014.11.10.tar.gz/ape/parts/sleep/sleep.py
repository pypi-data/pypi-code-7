
# python standard library
import datetime
from types import FloatType, IntType

# this package
from ape import BaseClass
from ape import ApeError
from ape import Component
from ape.parts.eventtimer import EventTimer, wait


IN_PWEAVE = __name__ == '__builtin__'


class TheBigSleep(Component):
    """
    A sleeper
    """
    def __init__(self, end=None, total=None, interval=1, verbose=True):
        """
        The Big Sleep's constructor

        :param:

         - `end`: a datetime object set for the end of the sleep
         - `total`: A timedelta set for the length of the sleep
         - `interval`: seconds between printing status
         - `verbose`: if True (default), print time-remaining at intervals
        """
        super(TheBigSleep, self).__init__()
        self._end = None
        self.end = end
        self._total = None
        self.total = total
        self.interval = interval
        self.verbose = verbose
        self._then = None
        self._zero = None
        self._minus_one = None
        self._timer = None
        return

    @property
    def end(self):
        """
        end datetime

        :return: datetime to stop
        """
        return self._end

    @end.setter
    def end(self, new_end):
        """
        Sets end and re-sets then to None

        :param:

         - `new_end`: datetime object set to time to stop

        :postcondition: self._then is None
        """
        self._end = new_end
        self._then = None
        return

    @property
    def total(self):
        """
        Timedelta representing relative time in the future to stop

        :return: timedelta to stop in the future or None
        """
        return self._total

    @total.setter
    def total(self, new_total):
        """
        Sets the total and re-sets the `then`

        :param:

         - `new_total`: timedelta for future stop time or None

        :postcondition:

         - `self._total` set to `new_total`
         - `self._then` is None
        """
        self._total = new_total
        self._then = None
        return

    @property
    def then(self):
        """
        the stopping-time

        :return: datetime set to future stop-time
        :raise: ApeError if neither end nor total is set
        """
        if self._then is None:
            if self.end is None and self.total is None:
                raise ApeError("either 'end' or 'total' must be set")
            if self.end is not None:
                self._then = self.end
            else:
                try:
                    self._then = datetime.datetime.now() + self.total
                except TypeError as error:
                    self.log_error(error)
                    raise ApeError("'TheBigSleep.total' cannot be '{0}'".format(self.total))
        return self._then

    @property
    def zero(self):
        """
        A zero timedelta

        :return: timedelta(0)
        """
        if self._zero is None:
            self._zero = datetime.timedelta()
        return self._zero

    @property
    def minus_one(self):
        """
        A -1 timedelta

        :return: timedelta that subtracts one second when added to another
        """
        if self._minus_one is None:
            self._minus_one = timedelta(seconds=-1)
        return self._minus_one

    @property
    def timer(self):
        """
        An EventTimer for the wait decorator

        :return: EventTimer with interval set to self.interval
        """
        if self._timer is None:
            self._timer = EventTimer(seconds=self.interval)
        return self._timer

    def __call__(self):
        """
        The main interface - blocks until time is up, emitting messages
        """
        remaining = self.then - datetime.datetime.now()
        
        self.logger.info("Sleeping for {0}".format(remaining))
        
        while remaining > self.zero:
            # there is a 1-second wait the  emit method blocks before emitting
            # so we have to let it calculate remaining or it will be 1-second behind
            remaining = self.emit()
        self.logger.info("Exiting Sleep")
        # this is to reset the end-time so it can be used more than once
        self._then = None
        return

    @wait
    def emit(self):
        """
        prints time remaining to stdout

        :return: timedelta of remaining time
        """
        remaining = max(self.then - datetime.datetime.now(), self.zero)
        if self.verbose:
            print "{0} Remaining".format(remaining)
        return remaining

    def check_rep(self):
        """
        Checks the paramaters

        :raise: ApeError if mis-configured
        """
        if self.end is None and self.total is None:
            raise ApeError("self.end and self.total cannot both be None")
        if type(self.interval) not in (FloatType, IntType):
            raise ApeError("self.interval must be float or int, not ({0}) {1}".format(type(self.interval),
                                                                                      self.interval))

    def close(self):
        """
        Closes the timer, sets self.then to 0.
        """
        self._then = self.zero
        self.timer.close()
        return
        
    def __str__(self):
        """
        a string representation
        """
        return "Sleep Until: {0}, checking at {1} second intervals".format(self.then,
                                                                           self.interval)

# end class TheBigSleep        


if IN_PWEAVE:
    from ape.parts.sleep.sleep import TheBigSleep
    print "A Module Diagram for **{0}**.\n".format(TheBigSleep.__module__)
    
    import os
    from ape.infrastructure.code_graphs import module_diagram, class_diagram
    this_file = os.path.join(os.getcwd(), 'sleep.py')
    module_diagram_file = module_diagram(module=this_file, project='thebigsleep')
    print ".. image:: {0}".format(module_diagram_file)



if __name__ == '__main__':
    total = datetime.timedelta(seconds=5)

    sleep = TheBigSleep(total=total, interval=1)
    #sleep.timer.clear()
    print 'sleeping for {0}'.format(sleep.total)
    print "Event is set: {0}".format(sleep.timer.event.is_set())
    sleep()
    end = datetime.datetime.now() + total
    sleep = TheBigSleep(end=end, interval=1)
    print 'sleeping until {0}'.format(sleep.then)
    print "Event is set: {0}".format(sleep.timer.event.is_set())
    sleep()
