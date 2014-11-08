import ctypes
import mmap
import os
from wicomm.SharedMemIf import SharedMemIf, memory_map
from wicomm.UdpDataSource import UdpDataSource

class SharedMemoryWriter:
    def __init__(self):
        self.data = {}
        self.dataSource = UdpDataSource()
        self.sharedMem = SharedMemIf
        self.mMapFile = memory_map
        self.initSharedMem()
        self.initData()

    def initSharedMem(self):
        fd = os.open(self.mMapFile, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        assert os.write(fd, '\x00' * mmap.PAGESIZE) == mmap.PAGESIZE
        self.buf = mmap.mmap(fd, mmap.PAGESIZE)

    def initData(self):
        for term in self.sharedMem:
            self.data[term["Name"]] = self.typeFromString(term["Type"]).from_buffer(self.buf, term["Offset"])

    def typeFromString(self, s):
        if s == 'f':
            return ctypes.c_float

    def update(self):
        unpacked_data = self.dataSource.update()
        #for term, value in zip(QuadSharedMem, unpacked_data):
        #    self.data[term["Name"]].value = value
        for term, value in zip(self.sharedMem, unpacked_data):
            self.data[term["Name"]].value = value
