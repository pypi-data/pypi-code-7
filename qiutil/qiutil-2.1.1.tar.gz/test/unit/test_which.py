import os
import glob
from nose.tools import (assert_is_none, assert_is_not_none, assert_true,
                        assert_false)
from ..helpers.logging import logger
from qiutil import which


class TestWhich(object):

    """which unit tests."""

    def test_which(self):
        python_path = which.which('python')
        assert_is_not_none(python_path,
                           'python is not discovered in the executable path')
        assert_true(which.is_executable(python_path), 'python is not considered executable')
        bogus_path = which.which('bogus')
        assert_is_none(bogus_path, "bogus is found in the executable path at: %s"
                                   % bogus_path)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
