from seantis.placemap import tests


class TestMapView(tests.IntegrationTestCase):

    def get_map_view(self, map=None):
        map = map or self.create_map()
        return map.unrestrictedTraverse('@@view')

    def test_no_sources(self):
        view = self.get_map_view()
        self.assertIn("No sources have been added yet.", view())
