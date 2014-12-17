import os
import glob
from nose.tools import (assert_is_none, assert_is_not_none)
from qiutil import which


class TestWhich(object):
    """which unit tests."""

    def test_which(self):
        python_path = which.which('python')
        assert_is_not_none(python_path, 'python is not discovered in the'
                                        ' executable path')
        bogus_path = which.which('bogus')
        assert_is_none(bogus_path, "bogus is found in the executable path"
                                   " at: %s" % bogus_path)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
