import os
import glob
from nose.tools import (assert_equal, assert_true)
from qiutil.logging import logger
from qidicom import (reader, meta)
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
"""The test image
 Series Number."""

SERIES_UID = '1.3.12.2.1107.5.2.32.35139.2010011914134225154552501.0.0.0'
"""The test image Series UID."""

INSTANCE_NBR = 6
"""The test image Instance Number."""


class TestReader(object):
    """The dicom reader unit tests."""

    def test_read_headers(self):
        # The first brain image.
        files = glob.glob(FIXTURE + '/*')
        # Read the tags.
        for ds in reader.iter_dicom_headers(FIXTURE):
            tdict = meta.select(ds, 'Study ID', 'Series Number')
            study = tdict['Study ID']
            assert_equal(study, STUDY_ID, "Study tag incorrect: %s" % study)
            series = tdict['Series Number']
            assert_equal(series, SERIES_NBR, "Series tag incorrect: %d" % series)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
