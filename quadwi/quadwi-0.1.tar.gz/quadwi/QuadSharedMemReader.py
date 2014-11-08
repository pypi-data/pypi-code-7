import mmap
import os
import struct
import time
from wicomm import SharedMemoryReader
from quadwi.QuadSharedMemIf import QuadSharedMemIf, quad_memory_map

class QuadSharedMemReader(SharedMemoryReader):
    def __init__(self):
        self.mMapFile = quad_memory_map
        self.sharedMem = QuadSharedMemIf
        self.initializeSharedMem()

