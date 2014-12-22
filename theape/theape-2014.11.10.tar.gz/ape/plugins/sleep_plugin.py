
# python standard library
from collections import OrderedDict

# third party
from configobj import ConfigObj

# this package
from ape import BasePlugin
from ape.parts.sleep.sleep import TheBigSleep
from ape.infrastructure.timemap import time_validator


SLEEP_SECTION = 'SLEEP'
END_OPTION = 'end'
TOTAL_OPTION = 'total'
INTERVAL_OPTION = 'interval'
VERBOSE_OPTION = 'verbose'


configuration = """
  [[SLEEP]]
  # to allow the section names to be arbitrary
  # the plugin names are required
  plugin = Sleep
  # 'end' should be a timestamp for the end-time (11-12-2013 8:45 pm)
  # 'total' should be a timestamp for the run-time (1 hr 23 minutes)
  # 'interval' should be <amount> <units> (1 minute)
  # if verbose is False, sceen output will be off except at startup
  # only one of absolute or relative time is required, although both can be used
  end = <absolute time>
  total = <relative time>
  interval = 1 second
  verbose = True
"""


sleep_configspec = """
end = absolute_time(default=None)
total = relative_time(default=None)
interval = relative_time(default=1)
verbose = boolean(default=True)
"""


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
        self._subsection = None
        return

    @property
    def subsection(self):
        """
        the plugin sub-section
        """
        if self._subsection is None:
            configspec = ConfigObj(sleep_configspec.splitlines(),
                                   list_values=False,
                                   _inspec=True)
            section = ConfigObj(self.configuration[self.section_header],
                                configspec=configspec)
            section.validate(time_validator)
            self._subsection = section
        return self._subsection
            

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
            end = self.subsection[END_OPTION]
            total = self.subsection[TOTAL_OPTION]
            interval = self.subsection[INTERVAL_OPTION]

            if interval != 1:
                interval = interval.total_seconds()
            verbose = self.subsection[VERBOSE_OPTION]
            self._product = TheBigSleep(end=end,
                                        total=total,
                                        interval=interval,
                                        verbose=verbose)
        return self._product
