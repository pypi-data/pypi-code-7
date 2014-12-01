from seantis.placemap import tests
from seantis.placemap import content


class TestTypes(tests.IntegrationTestCase):

    def test_create_types(self):
        map = self.create_map()
        self.assertIs(type(map.aq_base), content.Map)

        source = self.create_source(map)
        self.assertIs(type(source.aq_base), content.Source)
