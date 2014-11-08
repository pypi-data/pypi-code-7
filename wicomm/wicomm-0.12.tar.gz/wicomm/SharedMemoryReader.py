import mmap
import os
import struct
import time
from wicomm.SharedMemIf import SharedMemIf, memory_map

class SharedMemoryReader:
    def __init__(self):
        self.sharedMem = SharedMemIf
        self.mMapFile = memory_map
        self.initializeSharedMem()

    def initializeSharedMem(self):
        # Open the file for reading
        fd = os.open(self.mMapFile, os.O_RDWR)
        # Memory map the file
        self.buf = mmap.mmap(fd, mmap.PAGESIZE)

    def readData(self):
        returnDict = {}
        for term in self.sharedMem:
            returnDict[term["Name"]] = self.unloadData(self.buf, term)[0]
        return returnDict

    def unloadData(self, buf, term):
        return struct.unpack(term["Type"], buf[term["Offset"]:term["Offset"]+term["Size"]])
