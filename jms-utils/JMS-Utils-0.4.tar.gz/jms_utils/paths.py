import logging
import os
import sys

from jms_utils import FROZEN

log = logging.getLogger(__name__)


class ChDir(object):
    # Step into a directory temporarily. Then return to
    # orignal directory.
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        log.debug(u'Changing to Directory --> {}'.format(self.new_dir))
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        log.debug(u'Moving back to Directory --> {}'.format(self.old_dir))
        os.chdir(self.old_dir)


if FROZEN:  # pragma: no cover
    # we are running in a |PyInstaller| bundle
    cwd = os.path.dirname(sys.argv[0])
else:
    # we are running in a normal Python environment
    cwd = os.getcwd()
