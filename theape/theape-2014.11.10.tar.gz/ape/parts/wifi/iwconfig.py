
# The MIT License (MIT)
# 
# Copyright (c) 2013 Russell Nakamura
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# python standard library
import re

# this package
from ape import BaseClass, ApeError
from ape.parts.eventtimer import EventTimer
from ape.parts import oatbran


DECIBEL_MILLIWATTS = 'dBm'
KILO_MEGA_GIGA = 'kMG'
HERZ = 'Hz'
BITS_PER_SECOND = 'b/s'


class IwconfigEnum(object):
    """
    names for the regular expressions
    """
    __slots__ = ()
    essid = 'essid'
    mac_protocol = 'mac_protocol'
    mode = 'mode'
    frequency = 'frequency'
    access_point = 'access_point'
    bit_rate = 'bit_rate'
    tx_power = 'tx_power'
    link_quality = 'link_quality'
    signal_level = 'signal_level'
    rx_invalid_nwid = 'rx_invalid_nwid'
    rx_invalid_crypt = 'rx_invalid_crypt'
    rx_invalid_frag = 'rx_invalid_frag'
    tx_excessive_retries = 'tx_excessive_retries'
    invalid_misc = 'invalid_misc'
    missed_beacons = 'missed_beacons'
# end IwconfigEnum


class IwconfigExpressions(object):
    """
    Holds regular expressions to tokenize the output
    """
    def __init__(self, interface='wlan0'):
        """
        IwconfigExpressions constructor

        :param:

         - `interface`: the name of the interface to check (only used for MAC protocol)
        """
        self.interface = interface
        self._essid = None
        self._mac_protocol = None
        self._mode = None
        self._frequency = None
        self._access_point = None
        self._bit_rate = None
        self._tx_power = None
        self._link_quality = None
        self._signal_level = None
        self._rx_invalid_nwid = None
        self._rx_invalid_crypt = None
        self._rx_invalid_frag = None
        self._tx_excessive_retries = None
        self._invalid_misc = None
        self._missed_beacons = None
        return

    @property
    def essid(self):
        """        
        :return: compiled regular expression to match the essid

        SSID's can have just about anything, even spaces, slashes, etc.
        """
        if self._essid is None:
            self._essid = re.compile('ESSID:' +
                                     oatbran.Group.named(name=IwconfigEnum.essid,
                                                         expression=oatbran.CommonPatterns.everything))
        return self._essid

    @property
    def mac_protocol(self):
        """        
        :return: regex to match protocol (requires self.interface to be set)

        Because the protocol can contain spaces might catch a trailing space
        This could be fixed if you assume that it will always be 802.11
        """
        if self._mac_protocol is None:
            self._mac_protocol = re.compile(self.interface +
                                            oatbran.CommonPatterns.spaces +
                                            oatbran.Group.named(name=IwconfigEnum.mac_protocol,
                                                                expression=oatbran.CommonPatterns.everything) +
                                                                oatbran.CommonPatterns.spaces + 'ESSID:')
        return self._mac_protocol

    @property
    def mode(self):
        """
        :return: compiled regex to match the mode (e.g. Managed)
        """
        if self._mode is None:
            self._mode = re.compile("Mode:" +
                                    oatbran.Group.named(IwconfigEnum.mode,
                                                        oatbran.CommonPatterns.not_spaces) +
                                                        oatbran.CommonPatterns.spaces)
        return self._mode

    @property
    def frequency(self):
        """
        :return: compiled regex to get the frequency
        According to the man-page it might use channel instead of frequency
        but I have no examples of that right now        
        """
        if self._frequency is None:
            self._frequency = re.compile('Frequency:' +
                                         oatbran.Group.named(IwconfigEnum.frequency,
                                                             (oatbran.Group.group(oatbran.Numbers.real) +
                                                              oatbran.CommonPatterns.spaces +
                                                              oatbran.Quantifier.zero_or_more(oatbran.CharacterClass.character_class(KILO_MEGA_GIGA)) + 
                                                              HERZ)))
        return self._frequency

    @property
    def access_point(self):
        """
        :return: compiled regex to get the access point        
        the pattern matches anything not a space because ad-hoc mode won't return MAC
        """
        if self._access_point is None:
            self._access_point = re.compile('Access Point:' +
                                            oatbran.CommonPatterns.spaces +
                oatbran.Group.named(IwconfigEnum.access_point,
                                    oatbran.CommonPatterns.not_spaces) +
                oatbran.CommonPatterns.spaces)
        return self._access_point

    @property
    def bit_rate(self):
        """
        :return: expression to get the bit rate        
        According to the man-page 'Bit Rate=<value>' means it is fixed,
        'Bit Rate:<value>' means it can change        
        """
        if self._bit_rate is None:
            self._bit_rate = re.compile("Bit Rate" +
                                        oatbran.CharacterClass.character_class("=:") +
                                        oatbran.Group.named(IwconfigEnum.bit_rate,
                                                            (oatbran.Group.group(oatbran.Numbers.real)) +
                                                             oatbran.CommonPatterns.spaces +
                                                             oatbran.Quantifier.zero_or_more(oatbran.CharacterClass.character_class(KILO_MEGA_GIGA)) +
                                                             BITS_PER_SECOND))
        return self._bit_rate

    @property
    def tx_power(self):
        """
        :return: compiled regex to match the tx-power
        """
        if self._tx_power is None:
            # I don't know if this can be Tx-Power: or not
            self._tx_power = re.compile("Tx-Power=" +
                                        oatbran.Group.named(IwconfigEnum.tx_power,
                                                            (oatbran.Numbers.digits +
                                                             oatbran.CommonPatterns.spaces +
                                                             'dBm')))
        return self._tx_power

    @property
    def link_quality(self):
        """
        :return: compiled regular expression to get the link quality
        """
        if self._link_quality is None:
            self._link_quality = re.compile("Link Quality=" + 
                                            oatbran.Group.named(IwconfigEnum.link_quality,
                                                                (oatbran.Numbers.digits +
                                                                 '/' + oatbran.Numbers.digits)))
        return self._link_quality

    @property
    def signal_level(self):
        """
        :return: compiled regex to get the signal level
        """
        if self._signal_level is None:
            self._signal_level = re.compile('Signal level=' +
                                            oatbran.Group.named(IwconfigEnum.signal_level,
                                                                '-' + oatbran.Numbers.digits +
                                                                oatbran.CommonPatterns.spaces + DECIBEL_MILLIWATTS))
        return self._signal_level

    @property
    def rx_invalid_nwid(self):
        """
        :return: compiled regex to get count of invalid nwid
        Man Page: used to detect configuration problems or adjacent network existence        
        """
        if self._rx_invalid_nwid is None:
            self._rx_invalid_nwid = re.compile("Rx invalid nwid:" +
                                               oatbran.Group.named(IwconfigEnum.rx_invalid_nwid,
                                                                   oatbran.Numbers.digits))
        return self._rx_invalid_nwid

    @property
    def rx_invalid_crypt(self):
        """
        :return: compiled regex to get count of un-decryptable packets
        Man page: used to detect invalid encryption settings
        """
        if self._rx_invalid_crypt is None:
            self._rx_invalid_crypt = re.compile("Rx invalid crypt:" +
                                               oatbran.Group.named(IwconfigEnum.rx_invalid_crypt,
                                                                   oatbran.Numbers.digits))
        return self._rx_invalid_crypt

    @property
    def rx_invalid_frag(self):
        """
        :return: compiled regex to get count of invalid packet fragments
        man page: count of packets that hardware couldn't properly re-assemble link-layer fragments
        """
        if self._rx_invalid_frag is None:
            self._rx_invalid_frag = re.compile("Rx invalid frag:" +
                                               oatbran.Group.named(IwconfigEnum.rx_invalid_frag,
                                                                   oatbran.Numbers.digits))
        return self._rx_invalid_frag

    @property
    def tx_excessive_retries(self):
        """
        :return: compiled regex to get count of packets hardware failed to deliver
        """
        if self._tx_excessive_retries is None:
            self._tx_excessive_retries = re.compile("Tx excessive retries:" +
                                                    oatbran.Group.named(IwconfigEnum.tx_excessive_retries,
                                                                        oatbran.Numbers.digits))
        return self._tx_excessive_retries

    @property
    def invalid_misc(self):
        """
        :return: compiled regex to get count of packets lost for misc reasons
        """
        if self._invalid_misc is None:
            self._invalid_misc = re.compile('Invalid misc:' +
                                            oatbran.Group.named(IwconfigEnum.invalid_misc,
                                                                oatbran.Numbers.digits))
        return self._invalid_misc

    @property
    def missed_beacons(self):
        """
        :return: compiled regex to get count of beacons from Cell or AP missed
        man page: missed beacons usually means the card is out of range        
        """
        if self._missed_beacons is None:
            self._missed_beacons = re.compile('Missed beacon:' +
                                              oatbran.Group.named(IwconfigEnum.missed_beacons,
                                                                  oatbran.Numbers.digits))
        return self._missed_beacons
# end class IwconfigExpressions            


class IwconfigQuery(BaseClass):
    """
    Queries ``iwconfig`` for information
    """
    def __init__(self, connection, interface='wlan0', interval=0.5,
                 missing_data='NA'):
        """
        IwconfigQuery constructor

        :param:

         - `interface`: name of the interface to query
         - `connection`: connection to the device to query
         - `interval`: seconds to wait before refreshing output
         - `missing_data`: symbol to use if the expression fails to match
        """
        super(IwconfigQuery, self).__init__()
        self.interface = interface
        self.connection = connection
        self.interval = interval
        self.missing_data = missing_data
        self._expressions = None
        self._command = None
        self._event_timer = None
        return

    @property
    def expressions(self):
        """
        :return: IwconfigExpressions to parse output
        """
        if self._expressions is None:
            self._expressions = IwconfigExpressions(interface=self.interface)
        return self._expressions

    @property
    def event_timer(self):
        """
        An EventTimer to track intervals between calling iwconfig
        """
        if self._event_timer is None:
            self._event_timer = EventTimer(seconds=self.interval)
        return self._event_timer        

    @property
    def output(self):
        """
        Output of the iwconfig command, refreshed after self.interval second intervals
        """
        if self.event_timer.is_set():
            self._output = self()
            self.event_timer.start()
        return self._output

    @property
    def command(self):
        """
        :return: command to send to connection to query iwconfig
        """
        if self._command is None:
            self._command = 'iwconfig {0}'.format(self.interface)
        return self._command

    @property
    def essid(self):
        """
        :return: the essid from the iwconfig command
        """
        return self._check_output(expression=self.expressions.essid,
                                    name=IwconfigEnum.essid)
    
    @property
    def mac_protocol(self):
        """
        :return: the MAC protocol
        """
        return self._check_output(expression=self.expressions.mac_protocol,
                                  name=IwconfigEnum.mac_protocol)

    @property
    def mode(self):
        """
        :return: the mode
        """
        return self._check_output(expression=self.expressions.mode,
                                  name=IwconfigEnum.mode)

    @property
    def frequency(self):
        """
        :return: current frequency
        """
        return self._check_output(expression=self.expressions.frequency,
                                  name=IwconfigEnum.frequency)

    @property
    def access_point(self):
        """
        :return: MAC address of associated AP
        """
        return self._check_output(expression=self.expressions.access_point,
                                  name=IwconfigEnum.access_point)

    @property
    def bit_rate(self):
        """
        :return: bit-rate
        """
        return self._check_output(expression=self.expressions.bit_rate,
                                  name=IwconfigEnum.bit_rate)

    @property
    def tx_power(self):
        """
        :return: the TX-power for the node
        """
        return self._check_output(expression=self.expressions.tx_power,
                                  name=IwconfigEnum.tx_power)

    @property
    def link_quality(self):
        """
        :return: link-quality perceived by driver
        """
        return self._check_output(expression=self.expressions.link_quality,
                                  name=IwconfigEnum.link_quality)

    @property
    def signal_level(self):
        """
        :return: signal level (RSSI)
        """
        return self._check_output(expression=self.expressions.signal_level,
                                  name=IwconfigEnum.signal_level)

    @property
    def rx_invalid_nwid(self):
        """
        :return: count of packets with SSID's not matching current cell
        """
        return self._check_output(self.expressions.rx_invalid_nwid,
                                  IwconfigEnum.rx_invalid_nwid)

    @property
    def rx_invalid_crypt(self):
        """
        :return: count of packets not unencryptable
        """
        return self._check_output(self.expressions.rx_invalid_crypt,
                                  IwconfigEnum.rx_invalid_crypt)

    @property
    def rx_invalid_frag(self):
        """
        :return: count of packets whose fragments couldn't be re-assembled
        """
        return self._check_output(self.expressions.rx_invalid_frag,
                                  IwconfigEnum.rx_invalid_frag)

    @property
    def tx_excessive_retries(self):
        """
        :return: count of packets not successfully transmitted
        """
        return self._check_output(self.expressions.tx_excessive_retries,
                                  IwconfigEnum.tx_excessive_retries)

    @property
    def invalid_misc(self):
        """
        :return: count of invalid packets (received only?)
        """
        return self._check_output(self.expressions.invalid_misc,
                                  IwconfigEnum.invalid_misc)

    @property
    def missed_beacons(self):
        """
        :return: count of beacons not received
        """
        return self._check_output(self.expressions.missed_beacons,
                                  IwconfigEnum.missed_beacons)

    def _check_output(self, expression, name):
        """
        Helper method to traverse output

        :param:

         - `expression`: regular expression to match the tokne
         - `name`: group-name for matching cases

        :return: matched text or self.missing_data if not found
        """
        for line in self.output:
            match = expression.search(line)
            if match is not None:
                return match.group(name).rstrip()
        return self.missing_data

    def __call__(self):
        """
        Calls the iwconfig command and returns the output
        """
        stdin, stdout, stderr = self.connection.iwconfig(self.interface)
        self.check_errors(stderr)
        # the stdout is re-used if the calls are made more frequently than self.interval
        # so the iterator can't be used
        return stdout.readlines()

    def check_errors(self, stderr):
        """
        Checks for known errors

        :param:

         - `stderr`: file-like object for standard error
        :raise: ApeError if an error is found
        """
        for line in stderr:
            if 'No such device' in line:
                self.logger.error(line)
                raise ApeError("'{0}' is not a recognized interface".format(self.interface))
            if 'no wireless extensions' in line:
                self.logger.error(line)
                raise ApeError("'{0}' is not a wireless interface".format(self.interface))
            if 'command not found' in line:
                self.logger.error(line)
                raise ApeError("'iwconfig' doesn't seem to be installed on the path.".format(self.interface))
        return

    def close(self):
        """
        Closes the event timer
        """
        self.event_timer.close()
        return

    def __str__(self):
        """
        :return: output of iwconfig command un-parsed
        """
        return "".join(self.output)
# end class IwconfigQuery    


if __name__ == '__main__':
    expressions = IwconfigExpressions()
    import pudb; pudb.set_trace()
    test = 'Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0'
    match = expressions.rx_invalid_crypt.search(test)
