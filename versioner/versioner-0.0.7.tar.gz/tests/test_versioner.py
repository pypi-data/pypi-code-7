import os
from versioner import Versioner

class TestBadFile(object):
    def setUp(self):
        with open("BADFILE", "wb") as f:
            f.write("loremipsumdillum")

    def test_open_bad_file(self):
        v = Versioner()
        v.open("BADFILE")
        mayor, minor, revision = v.get_version_components()
        assert mayor == 0
        assert minor == 0
        assert revision == 1

    def tearDown(self):
        os.remove("BADFILE")