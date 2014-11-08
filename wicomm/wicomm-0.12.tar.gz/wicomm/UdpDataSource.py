import socket
import json
import struct
from wicomm.WirelessDataSource import WirelessDataSource
from wicomm.SharedMemIf import SharedMemIf

# Define Quad UDP server host and port. This is the client.
HOST, PORT = "localhost", 2106

class UdpDataSource(WirelessDataSource):


    def __init__(self):
        # init base class
        super(UdpDataSource, self).__init__()
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = HOST
        self.port = PORT
        self.apiId = {
            'ApiId' : 'UdpGateway'
        }


    def update(self):
        self.sock.sendto(json.dumps(self.apiId), (self.host, self.port))
        rcvdData = self.sock.recv(1024)
        # good debug print
        #print ":".join("{:02x}".format(ord(c)) for c in rcvdData)
        return struct.unpack_from(self.fmtString, rcvdData)
