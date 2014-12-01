import unittest
from test.config.config import config
from geobricks_gis_raster.core import raster

metadata_publish = {
    "uid": "fenix|layer_test",
    "meContent": {
        "resourceRepresentationType": "geographic",
    },
    "dsd": {
        "contextSystem": "FENIX",
        "workspace": "fenix",
        "layerName": "layer_test"
    }
}


class GeobricksTest(unittest.TestCase):

    def test_publish_coveragestore(self):
        print "here"

