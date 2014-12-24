#!/usr/bin/env python
# -*- coding: utf-8 -*-
import android_common
from config import Config

class MatipServer(object):
    def __init__(self,capabilities):
        self.fast_reset = Config.FAST_RESET
        try:
            self.app = capabilities["app"]
            self.pkg = capabilities["appPackage"]
            self.act = capabilities["appActivity"]
        except:
            msg = "app,appPackage,appActivity can't be none"
            raise Exception(msg)

    def start(self):
        self.installAppForTest()
        self.waitForServer()

    def installAppForTest(self):
        remote_apk = android_common.remoteApkIsExists(self.app)
        installed = android_common.isInstalled(self.pkg)
        if installed and remote_apk and self.fast_reset:
            android_common.resetApp(self.fast_reset,self.pkg)
        elif not installed or (self.fast_reset and not remote_apk):
            android_common.mkRemoteDir()
            remote_apk,md5 = android_common.getRemotePath(self.app)
            android_common.removeTempApks([md5])
            android_common.installRemoteWithRetry(remote_apk,self.pkg,self.app)

    def waitForServer(self):
        android_common.startApp(self.pkg,self.act)
        android_common.waitForActivityOn(self.pkg,self.act)
        

