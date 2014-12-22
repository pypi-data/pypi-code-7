
# python standard library
from collections import OrderedDict

# this package
from ape import BasePlugin
#from ape.parts.watchers import TheWatcher
from ape.parts.storage.filestorage import FileStorage


SECTION = 'WATCHER'
INTERVAL_OPTION = 'interval'
TOTAL_OPTION = 'total'
VERBOSE_OPTION = 'verbose'


configuration = """
[{0}]
# 
""".format(SECTION,
           TOTAL_OPTION,
           INTERVAL_OPTION,
           VERBOSE_OPTION)


sections = OrderedDict()
sections['name'] = '{bold}sleep{reset} -- a countdown timer that blocks until time is over'
sections['description'] = '{bold}sleep{reset} is a verbose no-op (by default) meant to allow the insertion of a pause in the execution of the APE. At this point all calls to sleep will get the same configuration.'
sections['configuration'] = configuration
sections['see also'] = 'EventTimer, RelativeTime, AbsoluteTime'
sections['options'] = """
The configuration options --

    {bold}end{reset} : an absolute time given as a time-stamp that can be interpreted by `dateutil.parser.parse`. This is for the cases where you have a specific time that you want the sleep to end.

    {bold}total{reset} : a relative time given as pairs of '<amount> <units>' -- e.g. '3.4 hours'. Most units only use the first letter, but since `months` and `minutes` both start with `m`, you have to use two letters to specify them. The sleep will stop at the start of the sleep + the total time given.

    {bold}interval{reset} : The amount of time beween reports of the time remaining (default = 1 second). Use the same formatting as the `total` option.

    {bold}verbose{reset} : If True (the default) then report time remaining at specified intervals while the sleep runs.

One of {bold}end{reset} or {bold}total{reset} needs to be specified. Everything else is optional.
"""
sections['author'] = 'ape'


class Sleep(BasePlugin):
    """
    A plugin for TheBigSleep
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor for Sleep
        """
        super(Sleep, self).__init__(*args, **kwargs)
        return

    def fetch_config(self):
        """
        prints a config-file sample
        """
        print configuration

    @property
    def sections(self):
        """
        Help dictionary
        """
        if self._sections is None:
            self._sections = sections
        return self._sections

    @property
    def product(self):
        """
        A built TheBigSleep object

        :return: TheBigSleep
        """
        if self._product is None:
            end = self.configuration.get_datetime(section=SLEEP_SECTION,
                                                  option=END_OPTION,
                                                  optional=True)
            total = self.configuration.get_relativetime(section=SLEEP_SECTION,
                                                    option=TOTAL_OPTION,
                                                    optional=True)
            interval = self.configuration.get_relativetime(section=SLEEP_SECTION,
                                                           option=INTERVAL_OPTION,
                                                           optional=True,
                                                           default=1)
            if interval != 1:
                interval = interval.total_seconds()
            verbose = self.configuration.get_boolean(section=SLEEP_SECTION,
                                                     option=VERBOSE_OPTION,
                                                     optional=True,
                                                     default=True)
            self._product = TheBigSleep(end=end,
                                        total=total,
                                        interval=interval,
                                        verbose=verbose)
        return self._product
