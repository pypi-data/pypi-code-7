# Copyright (C) 2014 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

import zmq.green as zmq
import gevent

import beeswarm
from beeswarm.server.reporting.base_logger import BaseLogger
from beeswarm.shared.message_enum import Messages
from beeswarm.shared.socket_enum import SocketNames


class LoggerTests(unittest.TestCase):
    def test_base_logger(self):
        context = beeswarm.shared.zmq_context
        processedSessionsPublisher = context.socket(zmq.PUB)
        processedSessionsPublisher.bind(SocketNames.PROCESSED_SESSIONS)

        test_list = []
        mockLogger = TestLogger({}, test_list)
        mockLogger.start()
        # force context switch to allow greenlet to start
        gevent.sleep()

        for _ in range(15):
            processedSessionsPublisher.send('TOPIC DATA')

        gevent.sleep(2)
        self.assertEqual(len(mockLogger.test_queue), 15)

        mockLogger.stop()
        # will except if the logger hangs.
        mockLogger.get(block=True, timeout=2)


class TestLogger(BaseLogger):
    def __init__(self, options, test_queue):
        super(TestLogger, self).__init__(options)
        self.test_queue = test_queue

    def handle_data(self, topic, data):
        self.test_queue.append(data)
