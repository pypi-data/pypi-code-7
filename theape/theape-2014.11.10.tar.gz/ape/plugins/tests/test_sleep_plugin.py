
# python standard library
import unittest

# third-party
from mock import MagicMock, call

# the ape
from ape.plugins.sleep_plugin import Sleep, END_OPTION, TOTAL_OPTION, INTERVAL_OPTION, VERBOSE_OPTION


class TestingSleepPlugin(unittest.TestCase):
    def setUp(self):
        self.config_map = MagicMock()
        self.section_header = 'sleeper'
        self.sleep = Sleep(configuration=self.config_map,
                           section_header=self.section_header)
        return

    def test_constructor(self):
        """
        Does it take the two expected parameters?
        """
        self.assertIs(self.config_map, self.sleep.configuration)
        self.assertIs(self.section_header, self.sleep.section_header)
        return

    def test_product(self):
        """
        Does it build the product in the way you expect?
        """
        product = self.sleep.product
        self.config_map.get_datetime.assert_called_with(section=self.section_header,
                                                        option=END_OPTION,
                                                        optional=True)
        calls = [call(section=self.section_header,option=TOTAL_OPTION,optional=True),
                 call(section=self.section_header,option=INTERVAL_OPTION,optional=True,default=1)]
        self.assertEqual(calls, self.config_map.get_relativetime.call_args_list)
        self.config_map.get_boolean.assert_called_with(section=self.section_header,
                                            option=VERBOSE_OPTION,
                                            optional=True,
                                            default=True)
        return    
