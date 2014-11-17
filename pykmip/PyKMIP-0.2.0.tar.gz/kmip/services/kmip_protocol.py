# Copyright (c) 2014 The Johns Hopkins University/Applied Physics Laboratory
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from struct import unpack

import binascii
import logging

from kmip.core.utils import BytearrayStream


class KMIPProtocol(object):
    HEADER_SIZE = 8

    def __init__(self, socket, buffer_size=1024):
        self.socket = socket
        self.logger = logging.getLogger(__name__)

    def write(self, data):
        if len(data) > 0:
            sbuffer = bytes(data)
            self.logger.debug('buffer: {0}'.format(binascii.hexlify(sbuffer)))
            self.socket.sendall(sbuffer)

    def read(self):
        header = self._recv_all(self.HEADER_SIZE)
        msg_size = unpack('!I', header[4:])[0]
        payload = self._recv_all(msg_size)
        return BytearrayStream(header + payload)

    def _recv_all(self, total_bytes_to_be_read):
        bytes_read = 0
        total_msg = b''
        while bytes_read < total_bytes_to_be_read:
            msg = self.socket.recv(total_bytes_to_be_read - bytes_read)
            if not msg:
                break
            bytes_read += len(msg)
            total_msg += msg
        if bytes_read != total_bytes_to_be_read:
            raise Exception("Expected {0} bytes, Received {1} bytes"
                            .format(total_bytes_to_be_read, bytes_read))
        return total_msg


class KMIPProtocolFactory(object):

    def getProtocol(self, socket):
        return KMIPProtocol(socket)
