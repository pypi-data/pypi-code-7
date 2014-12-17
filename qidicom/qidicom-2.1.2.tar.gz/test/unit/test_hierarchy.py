import os
import glob
from nose.tools import (assert_equal, assert_true)
import qidicom
from qiutil.logging import logger
from .. import ROOT

FIXTURE = os.path.join(ROOT, 'fixtures', 'dicom')
"""The test image parent directory."""

SBJ_ID = 'Sarcoma002'
"""The Subject ID."""

STUDY_ID = '1'
"""The test image Study ID."""

STUDY_UID = '1.3.12.2.1107.5.2.32.35139.30000010011316342567100000106'
"""The test image Study UID."""

SERIES_NBR = 11
"""The test image Series Number."""

SERIES_UID = '1.3.12.2.1107.5.2.32.35139.2010011914134225154552501.0.0.0'
"""The test image Series UID."""

INSTANCE_NBR = 6
"""The test image Instance Number."""


class TestHierarchy(object):
    """The dicom hierarchy unit tests."""

    def test_hierarchy(self):
        paths = list(qidicom.hierarchy.read_hierarchy(FIXTURE))
        assert_equal(len(paths), 1,
                     "The DICOM Helper image hierarchy path count is incorrect")
        path = paths[0]
        assert_equal(len(path), 4,
                     "The DICOM Helper image path item count is incorrect")
        sbj_id, study_uid, series_uid, inst_nbr = path
        assert_equal(sbj_id, SBJ_ID, "Subject ID incorrect: %s" % sbj_id)
        assert_equal(study_uid, STUDY_UID,
                     "Study UID incorrect: %s" % study_uid)
        assert_equal(series_uid, SERIES_UID,
                     "Series UID incorrect: %s" % series_uid)
        assert_equal(inst_nbr, INSTANCE_NBR,
                     "Instance Number incorrect: %s" % inst_nbr)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
