import responses

from seantis.placemap import tests
from seantis.placemap import utils


class TestKML(tests.IntegrationTestCase):

    def test_kml_fixes(self, map=None):
        self.assertEqual(
            utils.fix_common_kml_problems('type="xsd:string"'),
            'type="string"'
        )

    def test_invalid_url(self):
        self.assertEqual(utils.fetch_kml_document('asdf'), None)

    @responses.activate
    def test_valid_url(self):
        responses.add(
            responses.GET, 'http://seantis.ch/kml',
            status=200, content_type='text/plain',
            body=(
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<kml xmlns="http://earth.google.com/kml/2.2">'
                '<Placemark>'
                '<Point>'
                '<coordinates>0.0,0.0,0</coordinates>'
                '</Point>'
                '</Placemark>'
                '</kml>'
            )
        )

        self.assertNotEqual(
            utils.fetch_kml_document('http://seantis.ch/kml'), None
        )
