import os
import glob
import shutil
from nose.tools import (assert_equal, assert_true)
from dicom import datadict as dd
from qidicom import (reader, meta)
from .. import ROOT
from ..helpers.logging import logger

FIXTURE = os.path.join(ROOT, 'fixtures', 'dicom')
"""The test fixture."""

RESULTS = os.path.join(ROOT, 'results', 'dicom')
"""The test results directory."""


class TestMeta(object):
    """
    The dicom meta unit tests.
    
    :Note: these tests also indirectly test the writer module.
    """

    def setUp(self):
        shutil.rmtree(RESULTS, True)

    def tearDown(self):
        shutil.rmtree(RESULTS, True)

    def test_edit_metadata(self):
        # The tag name => value map.
        tnv = dict(PatientID='Test Patient', BodyPartExamined='HIP')
        # The tag => value map.
        tv = {dd.tag_for_name(name): value for name, value in tnv.iteritems()}
        # Edit the headers.
        files = set(meta.edit(FIXTURE, dest=RESULTS, **tnv))

        # Verify the result.
        for ds in reader.iter_dicom(RESULTS):
            assert_true(ds.filename in files, "Edit result not found: %s" % ds.filename)
            for t, v in tv.iteritems():
                assert_equal(v, ds[t].value)


if __name__ == "__main__":
    import nose
    nose.main(defaultTest=__name__)
