import socket
import json
import struct
from wicomm.UdpDataSource import UdpDataSource
from quadwi.QuadSharedMemIf import QuadSharedMemIf

class QuadUdpDataSource(UdpDataSource):

    def __init__(self):
        # init base class
        super(QuadUdpDataSource, self).__init__()
        self.host = "localhost"
        self.port = 2106
        self.apiId = {
            'ApiId': 'QuadUdpGateway'
        }