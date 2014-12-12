# coding:utf-8
import logging

from scalr_manage import version
from scalr_manage.constant import VERSION_FLAG_FILE_EXT
from scalr_manage.library.base import Target


logger = logging.getLogger(__name__)


class MatchVersionTarget(Target):
    name = "match-version"
    help = "Check if the current configuration file version matches the current installer version"

    def __call__(self, args, ui, tokgen):
        exit_code = 0

        try:
            with open(".".join([args.configuration, VERSION_FLAG_FILE_EXT])) as f:
                if f.read() != version.__version__:
                    exit_code = 1
        except IOError:
            exit_code = 1

        raise SystemExit(exit_code)
