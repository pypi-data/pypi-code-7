
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2009-2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test class of 3Par Client handling Ports."""

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.abspath('../')))

import HP3ParClient_base as hp3parbase


class HP3ParClientPortTestCase(hp3parbase.HP3ParClientBaseTestCase):

    def setUp(self):
        super(HP3ParClientPortTestCase, self).setUp()

    def tearDown(self):
        super(HP3ParClientPortTestCase, self).tearDown()

    def test_get_ports_all(self):
        self.printHeader('get_ports_all')
        ports = self.cl.getPorts()
        if ports:
            if len(ports['members']) == ports['total']:
                self.printFooter('get_ports_all')
                return
            else:
                self.fail('Number of ports in invalid.')
        else:
            self.fail('Cannot retrieve ports.')

    def test_get_ports_fc(self):
        self.printHeader('get_ports_fc')
        fc_ports = self.cl.getFCPorts(4)
        print(fc_ports)
        if fc_ports:
            for port in fc_ports:
                if port['protocol'] != 1:
                    self.fail('Non-FC ports detected.')
            self.printFooter('get_ports_fc')
            return
        else:
            self.fail('Cannot retrieve FC ports.')

    def test_get_ports_iscsi(self):
        self.printHeader('get_ports_iscsi')
        iscsi = self.cl.getiSCSIPorts(4)
        if iscsi:
            for port in iscsi:
                if port['protocol'] != 2:
                    self.fail('Non-iSCSI ports detected.')
            self.printFooter('get_ports_iscsi')
            return
        else:
            self.fail('Cannot retrieve iSCSI Ports.')

    def test_get_ports_ip(self):
        self.printHeader('get_ports_ip')

        ip = self.cl.getIPPorts()
        if ip:
            for port in ip:
                if port['protocol'] != 4:
                    self.fail('non-ip ports detected.')
            self.printFooter('get_ports_ip')
        else:
            self.fail('cannot retrieve ip ports.')
