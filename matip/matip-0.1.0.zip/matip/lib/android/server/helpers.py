#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.sysconfig import get_python_lib

def getAndroidPlatform():
    sdk_root = os.environ.has_key("ANDROID_HOME")
    res = None
    if sdk_root:
        sdk_root_path = os.environ["ANDROID_HOME"]
        locs = ['android-4.2', 'android-17', 'android-4.3', 'android-18','android-4.4', 'android-19']
        for loc in locs:
            platforms = os.path.join(sdk_root_path,"platforms")
            platform = loc
            if res == None and os.path.exists(os.path.join(platforms,platform)):
                res = [platform,os.path.join(platforms,platform)]
    else:
        platform = "android-18"
        android_jar = "%s\\matip\\build\\selendroid" % get_python_lib()
        res = [platform,android_jar]
    return res

def testZipArchive(zip_path):
    return os.path.exists(zip_path)
