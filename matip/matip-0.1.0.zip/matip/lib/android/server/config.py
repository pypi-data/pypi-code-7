#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
class Config(object):
    FAST_RESET = True
    SYSTEM_PORT = 5555
    DEVICE_PORT = 8080
    PROXY_HOST = "127.0.0.1"
    if platform.system() is "Windows":
        TEMP_DIR = "C:\\Windows\\Temp"
    else:
        TEMP_DIR = "/tmp"
