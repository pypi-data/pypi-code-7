import socket
import json
import struct
from wicomm.SharedMemIf import SharedMemIf

# Define Quad UDP server host and port. This is the client.
HOST, PORT = "localhost", 2106

class WirelessDataSource(object):

    def __init__(self):
        self.fmtString = ''
        self.sharedMem = SharedMemIf
        self.convertToFmtString()

    def convertToFmtString(self):
        for sharedTerm in self.sharedMem:
            self.fmtString += sharedTerm["Type"]

    # Intended to be over-ridden in derived classes.
    def update(self):
        print "Wireless Data Source base class no implementation."
