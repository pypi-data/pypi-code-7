""" smashlib.modpath
"""
import sys

from report import report
from goulash._inspect import getcaller

class ModPath(list):
    """ a wrapper you can install around sys.path,
        very useful when debugging ipy_venv.
    """
    transactions = {}

    def _log_change(self, *args):
        caller_info1 = getcaller(2)
        caller_info = getcaller(3)
        report("sys.path.{0} initiated by {1}.{2}".format(
            caller_info1['func_name'],
            caller_info['class'], caller_info['func_name']))

    def __setitem__(self, x, y):
        self._log_change()
        return super(ModPath,self).__setitem__(x, y)

    def append(self, x):
        if x not in self:
            self._log_change()
            return super(ModPath,self).append(x)

    def remove(self, x):
        self._log_change()
        return super(ModPath, self).remove(x)

    @classmethod
    def install(kls):
        """ """
        if not isinstance(sys.path, kls):
            tmp = kls(sys.path)
            sys.path = tmp
        return sys.path
