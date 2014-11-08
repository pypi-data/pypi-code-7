import ctypes
import mmap
import os
from wicomm import SharedMemoryWriter
from quadwi.QuadSharedMemIf import QuadSharedMemIf, quad_memory_map
from quadwi.QuadUdpDataSource import QuadUdpDataSource

class QuadSharedMemWriter(SharedMemoryWriter):
    def __init__(self):
        self.data = {}
        self.dataSource = QuadUdpDataSource()
        self.sharedMem = QuadSharedMemIf
        self.mMapFile = quad_memory_map
        self.initSharedMem()
        self.initData()
