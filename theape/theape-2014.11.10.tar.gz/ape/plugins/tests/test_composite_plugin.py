
# python standard library
import unittest

# third-party
from mock import MagicMock, call

# the ape
from ape.plugins.watcherplugin import Watcher


class TestingWatcherPlugin(unittest.TestCase):
    def setUp(self):
        self.config_map = MagicMock()
        self.section_header = 'iliketowatch'
        self.plugin = Watcher(configuration=self.config_map,
                              section_header=self.section_header)
        return

    def test_constructor(self):
        """
        Does it take the two expected parameters?
        """
        self.assertIs(self.config_map, self.plugin.configuration)
        self.assertIs(self.section_header, self.plugin.section_header)
        return

    def test_product(self):
        """
        Does it build the product in the way you expect?
        """
        product = self.plugin.product
        self.config_map.items.assert_called_with(section=self.section_header,
                                                        optional=True,
                                                        default={})
        return    
