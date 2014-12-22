
# python standard library
import unittest
from StringIO import StringIO
import time

# third party
from mock import MagicMock

# this package
from ape.parts.wifi.iwconfig import IwconfigQuery, IwconfigExpressions
from ape.parts.wifi.iwconfig import IwconfigEnum
from ape import ApeError


try:
    source = open('iwconfig.txt').read()
    source2 = source.replace('simio_claustro', 'great_ape_ape')
    source_not_associated = open('iwconfig_not_associated.txt').read()
except IOError:
    # sphinx will crash on trying to import this module
    pass


class TestIwconfig(unittest.TestCase):
    def setUp(self):
        self.interface = 'wlan2'
        self.connection = MagicMock()
        self.connection.iwconfig.return_value = (None,
                                                 StringIO(source),
                                                 '')

        self.disconnected = (None,
                             StringIO(source_not_associated),
                             '')
        self.connection2 = MagicMock()
        self.connection2.iwconfig.return_value = self.disconnected
        self.iwconfig_disconnected = IwconfigQuery(interface=self.interface,
                                      connection=self.connection2)
        self.iwconfig = IwconfigQuery(interface=self.interface,
                                      connection=self.connection)
        return

    def test_constructor(self):
        """
        Does it build correctly?        
        """
        self.assertEqual(self.interface, self.iwconfig.interface)
        self.assertEqual(self.connection, self.iwconfig.connection)
        return

    def test_command(self):
        """
        Does it send the right command?
        """
        self.assertEqual('iwconfig wlan2', self.iwconfig.command)
        return

    def test_call(self):
        """
        Does it send the command and return the output?
        """
        output = self.iwconfig()
        self.assertEqual(output, StringIO(source).readlines())
        return

    def test_check_errors(self):
        """
        Does it raise the ApeError if appropriate?
        """
        # non-existent interface
        self.connection.iwconfig.return_value = (None, StringIO(source),
                                                 StringIO('wlan0      No such device'))
        self.assertRaises(ApeError, self.iwconfig)

        # non-wireless interface
        self.connection.iwconfig.return_value = (None, StringIO(source),
                                                 StringIO('wlan0      no wireless extensions.'))
        self.assertRaises(ApeError, self.iwconfig)

        # device doesn't have iwconfig
        # non-wireless interface
        self.connection.iwconfig.return_value = (None, StringIO(source),
                                                 StringIO('iwconfig:      command not found'))
        self.assertRaises(ApeError, self.iwconfig)
        return

    def test_output(self):
        """
        Does the output get set if checked after a certain time interval?
        """
        # two calls in rapid succession
        outputs = [(None, StringIO(source2),''),
                   (None, StringIO(source), '')]
        def side_effect(*args, **kwargs):
            return outputs.pop()
        self.connection.iwconfig.side_effect = side_effect
        self.assertEqual(self.iwconfig.output,
                         StringIO(source).readlines())
        self.assertEqual(self.iwconfig.output,
                         StringIO(source).readlines())

        # two calls outside the time
        outputs = [(None, StringIO(source2),''),
                   (None, StringIO(source), '')]
        def side_effect(*args, **kwargs):
            return outputs.pop()
        self.iwconfig._event_timer = None
        self.iwconfig.interval = 0
        self.connection.iwconfig.side_effect = side_effect
        self.assertEqual(self.iwconfig.output,
                         StringIO(source).readlines())
        time.sleep(0.1)
        self.assertEqual(self.iwconfig.output,
                         StringIO(source2).readlines())

        return

    def test_essid(self):
        """
        Does it get the name of the ap?
        """
        self.assert_equal('"simio_claustro"', self.iwconfig.essid)

        # disconnected case
        self.assert_equal("off/any", self.iwconfig_disconnected.essid)
        return

    def test_mac_protocol(self):
        """
        Does it get the MAC-protocol?
        """
        self.assert_equal('IEEE 802.11abgn', self.iwconfig.mac_protocol)
        return

    def test_mode(self):
        """
        Does it get the mode?
        """
        self.assert_equal('Managed', self.iwconfig.mode)
        return

    def test_frequency(self):
        """
        Does it get the frequency or NA if not connected?
        """
        self.assert_equal('2.462 GHz', self.iwconfig.frequency)

        # field disappears if not connected
        self.assert_equal(self.iwconfig.missing_data,
                          self.iwconfig_disconnected.frequency)        
        return

    def test_access_point(self):
        """
        Does it get the MAC address (or 'Not-Associated')
        """
        self.assert_equal('00:30:44:07:B2:92', self.iwconfig.access_point)
        # check Not-associated
        self.assert_equal('Not-Associated', self.iwconfig_disconnected.access_point)
        return

    def test_bit_rate(self):
        """
        Does it get the bit-rate or NA?
        """
        self.assert_equal('36 Mb/s', self.iwconfig.bit_rate)
        return

    def test_tx_power(self):
        """
        Does it get the tx-power?
        """
        self.assert_equal('15 dBm', self.iwconfig.tx_power)
        return

    def test_link_quality(self):
        """
        Does it get the link-quality?
        """
        self.assertEqual('40/70', self.iwconfig.link_quality)
        return

    def test_signal_level(self):
        """
        Does it get the RSSI?
        """
        self.assert_equal('-70 dBm', self.iwconfig.signal_level)
        return

    def test_rx_invalid_nwid(self):
        """
        Does it get the count of invalid SSID's?
        """
        self.assert_equal('0', self.iwconfig.rx_invalid_nwid)
        return

    def test_rx_invalid_crypt(self):
        self.assertEqual('0', self.iwconfig.rx_invalid_crypt)
        return

    def test_rx_invalid_frag(self):
        self.assertEqual('0', self.iwconfig.rx_invalid_frag)
        return

    def test_tx_excessive_retries(self):
        self.assertEqual('65239', self.iwconfig.tx_excessive_retries)
        return

    def test_invalid_misc(self):
        self.assertEqual('855', self.iwconfig.invalid_misc)
        return

    def test_missed_beacons(self):
        self.assertEqual('0', self.iwconfig.missed_beacons)
        return

    def test_missing_data(self):
        """
        Does it use the 'missing_data' property if the field is missing?
        """
        self.assertEqual(self.iwconfig.missing_data,
                         self.iwconfig_disconnected.signal_level)
        return

    def test_str(self):
        """
        Does the __str__ just return all the lines?
        """
        self.assert_equal(source, str(self.iwconfig))

    def assert_equal(self, expected, actual):
        self.assertEqual(expected, actual,
                         msg="Expected: {0}, Actual: {1}".format(expected, actual))


class TestIwconfigExpressions(unittest.TestCase):
    def setUp(self):
        self.expressions = IwconfigExpressions(interface='wlan2')
        return

    def test_constructor(self):
        """
        Will it build?
        """
        self.assertEqual('wlan2', self.expressions.interface)
        return

    def test_essid(self):
        """
        Does it match the essid?
        """
        match = self.expressions.essid.search(source)
        self.assertEqual('"simio_claustro"', match.group(IwconfigEnum.essid).strip())

        # disconnected
        match = self.expressions.essid.search(source_not_associated)
        self.assertEqual('off/any', match.group(IwconfigEnum.essid).strip())
        return

    def test_mac_protocol(self):
        """
        Does it get the protocol?
        """
        match = self.expressions.mac_protocol.search(source)
        self.assertEqual('IEEE 802.11abgn ', match.group(IwconfigEnum.mac_protocol))
        return

    def test_mode(self):
        """
        Does in get the mode?
        """
        match = self.expressions.mode.search(source)
        self.assertEqual('Managed', match.group(IwconfigEnum.mode))
        return

    def test_frequency(self):
        """
        Does it match the frequency?
        """
        match = self.expressions.frequency.search(source)
        self.assertEqual('2.462 GHz', match.group(IwconfigEnum.frequency))
        return

    def test_access_point(self):
        """
        Does it get the access points mac?
        """
        match = self.expressions.access_point.search(source)
        self.assertEqual("00:30:44:07:B2:92",
                         match.group(IwconfigEnum.access_point))
        return

    def test_bit_rate(self):
        """
        Does it get the bit rate?
        """
        match = self.expressions.bit_rate.search(source)
        self.assertEqual(match.group(IwconfigEnum.bit_rate),
                         "36 Mb/s")
        return

    def test_tx_power(self):
        """
        Does it get the tx-power?
        """
        match = self.expressions.tx_power.search(source)
        self.assertEqual('15 dBm', match.group(IwconfigEnum.tx_power))
        return

    def test_link_quality(self):
        """
        Does it get the link quality?
        """
        match = self.expressions.link_quality.search(source)
        self.assertEqual('40/70', match.group(IwconfigEnum.link_quality))
        return

    def test_signal_level(self):
        """
        Does it get the signal level?
        """
        match = self.expressions.signal_level.search(source)
        self.assertEqual('-70 dBm', match.group(IwconfigEnum.signal_level))
        return

    def test_rx_invalid_nwid(self):
        """
        Does it get the count of invalid network ids?
        """
        match = self.expressions.rx_invalid_nwid.search(source)
        self.assertEqual(match.group(IwconfigEnum.rx_invalid_nwid), '0')
        return

    def test_rx_invalid_crypt(self):
        """
        Does it get count of packets not decryptable?
        """
        match = self.expressions.rx_invalid_crypt.search(source)
        self.assertEqual(match.group(IwconfigEnum.rx_invalid_crypt),
                         '0')
        return

    def test_rx_invalid_frag(self):
        """
        Does it get count of packets that couldn't be reassembled?
        """
        match = self.expressions.rx_invalid_frag.search(source)
        return

    def test_tx_excessive_retries(self):
        """
        Does it get number of packets which hardware failed to deliver?
        """
        match = self.expressions.tx_excessive_retries.search(source)
        self.assertEqual(match.group(IwconfigEnum.tx_excessive_retries),
                         '65239')
        return

    def test_invalid_misc(self):
        """
        Does it get count of other packets lost because of wireless stuff?
        """
        match = self.expressions.invalid_misc.search(source)
        self.assertEqual(match.group(IwconfigEnum.invalid_misc),
                         '855')
        return

    def test_missed_beacons(self):
        """
        Does it get the count of missed beacons?
        """
        match = self.expressions.missed_beacons.search(source)
        return
