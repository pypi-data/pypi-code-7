
# python standard library
import datetime
from datetime import timedelta

# third party
import numpy

# this package
from ape import BaseClass, ApeError
from ape.infrastructure.strings import BOLD, RESET


DEBUG = 'debug'
INFO = 'info'
STAT_STRING = 'Time Stats -- Min: {min}, Q1: {q1}, Med: {med}, Q3: {q3}, Max: {max}, Mean: {mean}, StD: {std}'
ELAPSED_STRING = '{0}Elapsed Time:{1} {{0}}'.format(BOLD, RESET)
TOTAL_ELAPSED_STRING = '{0}Total Elapsed Time:{1} {{0}}'.format(BOLD, RESET)
ESTIMATED_REMAINING = '{0}Estimated Remaining Time:{1} {{0}}'.format(BOLD,
                                                                     RESET)
REPETITIONS_REMAINING = "{0}Repetitions Remaining:{1} {{0}}".format(BOLD, RESET)
TIME_LIMIT = "{0}Time-Limit Reached:{1} {{0}}".format(BOLD, RESET)
TIME_REMAINING = "{0}Time-Out Request in:{1} {{0}}".format(BOLD, RESET)
HARD_TIMEOUT = "{0}Absolute Quit at:{1} {{0}}".format(BOLD, RESET)
END_TIME = "{0}End-Time Reached:{1} {{0}}".format(BOLD, RESET)
MIN_PERCENTILE = 0
Q1_PERCENTILE = 25
MEDIAN_PERCENTILE = 50
Q3_PERCENTILE = 75
MAX_PERCENTILE = 100

CONTINUE = True
STOP = False
NOT_SET = None
UNSET = None
DECREMENT = -1
FINISHED = 0
ANNIHILATE = None


class TimeTracker(BaseClass):
    """
    A tracker of elapsed time
    """
    def __init__(self, log_level=DEBUG):
        """
        :param: `log_level`: level at which to report elapsed times (default='debug')
        """
        super(TimeTracker, self).__init__()
        self._logger = None
        self.log_level = log_level
        self.start = None
        self._times = None
        self._log = None
        return

    @property
    def times(self):
        """
        collection of elapsed times
        """
        if self._times is None:
            self._times = []
        return self._times

    @times.setter
    def times(self, times):
        """
        :param: ``times`` - collection
        :postcondition: self._times set to times
        """
        self._times = times
        return

    @property
    def log(self):
        """
        The logger method indicated by the log_level

        :return: logger.debug or logger.info
        """
        if self._log is None:
            if self.log_level == INFO:
                self._log = self.logger.info
            elif self.log_level == DEBUG:
                self._log = self.logger.debug
            else:
                raise ApeError("Unknown log level: {0}".format(self.log_level))
        return self._log
        

    def append(self, item):
        """
        Appends the item to the times array

        :param:

         - `item`: item to append to self.times (a numpy array)

        :postcondition: self.times contains item
        """
        self.times = numpy.append(self.times, [item])
        return

    def percentile(self, percentile):
        """
        calculates the percentile (e.g. 50 gets the median (the 50% item))

        :return: value for percintile of self.times as a timedelta
        """
        return timedelta(seconds=numpy.percentile(self.times, percentile))

    def log_update(self, elapsed):
        """
        Outputs to the log the most recent elapsed time information

        :param:

         - `elapsed`: timedelta
        """

        elapsed_string = ELAPSED_STRING.format(elapsed)
        self.log(elapsed_string)
        self.log(STAT_STRING.format(min=self.percentile(MIN_PERCENTILE),
                                    q1=self.percentile(Q1_PERCENTILE),
                                    med=self.percentile(MEDIAN_PERCENTILE),
                                    q3=self.percentile(Q3_PERCENTILE),
                                    max=self.percentile(MAX_PERCENTILE),
                                    mean=timedelta(seconds=numpy.mean(self.times)),
                                    std=timedelta(seconds=numpy.std(self.times))))
        return


    def __call__(self):
        """
        The main interface - starts and stops (toggles) the timer

        :return: True if starting, False if stopping
        :postcondition: elapsed time logged and added to self.times
        """
        if self.start is None:
            self.start = datetime.datetime.now()            
            return True
        elapsed = datetime.datetime.now() - self.start
        # numpy can't handle timedeltas
        self.append(elapsed.total_seconds())
        self.start = None
        self.log_update(elapsed)
        return False


class CountdownTimer(TimeTracker):
    """
    A time-tracker that counts down
    """
    def __init__(self, repetitions=1, end_time=None, total_time=None,
                 *args, **kwargs):
        """
        :param:

         - ``repetitions``: number of calls to accept before stopping
         - ``end_time``: datetime to stop
         - ``total_time``: timedelta for amount of time to run
        """
        super(CountdownTimer, self).__init__(*args, **kwargs)
        self.repetitions = repetitions
        self.end_time = end_time
        self.total_time = total_time
        self.last_time = None
        return

    def time_remains(self):
        """
        Evaluates if there is still time (or repetitions) remaining

        :precondition: if total_time is set, self.start is set
        :return: True if reps or time remains, False otherwise
        """
        this_time = datetime.datetime.now()
        # check that the parameters have been set
        if not any((self.end_time, self.total_time, self.repetitions)):
            return STOP

        if self.end_time is not UNSET:            
            if this_time >= self.end_time:
                # end-time takes first-precedence
                self.log(END_TIME.format(self.end_time))
                return STOP
            self.log(HARD_TIMEOUT.format(self.end_time))

        if self.total_time is not UNSET:
            # total_time is a relative time so it has to be on the LHS (need to fix this)
            if self.total_time <= (this_time - self.start):
                # total-time takes precedence over repetitions
                self.log(TIME_LIMIT.format(self.total_time))
                return STOP
            self.log(TIME_REMAINING.format(self.total_time - (this_time - self.start)))
            
        if self.repetitions is not UNSET:
            self.repetitions += DECREMENT
            if self.repetitions <= FINISHED:
                return STOP
            self.log(REPETITIONS_REMAINING.format(self.repetitions))
            
        # of no stopping-condtions are met, assume time-remains
        return CONTINUE

    def log_estimated_time_remaining(self):
        """
        Log an estitmated remaining time based on the median and repetitions  x xx 
        """
        this_time = datetime.datetime.now()
        if not any((self.end_time, self.total_time, self.repetitions)):
            self.log(ESTIMATED_REMAINING.format(0))
            return

        estimated_end = estimated_total = estimated_reps = timedelta.max

        if self.end_time is not UNSET:
            estimated_end = self.end_time - this_time
        if self.total_time is not UNSET:
            estimated_total = self.total_time - (this_time - self.start)
        if self.repetitions is not UNSET:
            estimated_reps = (self.repetitions *
                              self.percentile(MEDIAN_PERCENTILE))
            
        self.log(ESTIMATED_REMAINING.format(min(estimated_end,
                                                estimated_total,
                                                estimated_reps)))
        return

    def __call__(self):
        """
        The main interface. Each call re-starts the timer and decrements the repetitions

        :return: True if repetitions > 0, False otherwise
        """
        call_time = datetime.datetime.now()
        
        if self.start is NOT_SET:
            self.start = self.last_time = call_time
            return CONTINUE

        # convert to seconds so numpy can calculate statistics
        elapsed, self.last_time = call_time - self.last_time, call_time

        self.append(elapsed.total_seconds())
        self.log_update(elapsed)
        
        if self.time_remains():
            self.log_estimated_time_remaining()
            return CONTINUE

        # out of time or repetitions, tear it down
        self.log(TOTAL_ELAPSED_STRING.format(call_time-self.start))
        self.close()
        return STOP    

    def close(self):
        """
        Resets the attributes (makes __call__ always evaluate to false, not once like default)

        :postcondition:

         - ``self.end_time`` is None
         - ``self.total_time`` is None
         - ``self.repetitions`` is 0
         - ``self.start`` is None
         - ``self._times`` is None
        """
        self.start = UNSET
        self.end_time = UNSET
        self.total_time = UNSET
        self.repetitions = 0
        self._times = None
        return
# end class CountdownTimer
