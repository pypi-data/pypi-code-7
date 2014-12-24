#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import re
import time
import android_common
from config import Config
from distutils.sysconfig import get_python_lib
from matip.lib.android.common import log
from matip.lib.android.common import proxy
from matip.lib.android.common.command import Command

class SelendroidServer(object):
    def __init__(self,capabilities):
        self.mod_server_exists = False
        self.mod_app_pkg = None
        self.mod_server_timestamp = None
        self.server_apk = None
        self.fast_reset = Config.FAST_RESET
        self.system_port = Config.SYSTEM_PORT
        self.device_port = Config.DEVICE_PORT
        self.proxy_host = Config.PROXY_HOST
        self.proxy_port = self.system_port
        self.skip_uninstall = self.fast_reset
        try:
            self.local_apk = capabilities["app"]
            self.pkg = capabilities["appPackage"]
            self.activity = capabilities["appActivity"]
        except:
            msg = "app,appPackage,appActivity can't be none"
            raise Exception(msg)
        self.temp_dir = Config.TEMP_DIR
        self.selendroid_server_path = "%s\\selendroid.%s.apk" % (self.temp_dir,self.pkg)
        self.caps = capabilities

    def start(self):
        self.ensureServerExists()
        self.checkInternetPermissionForApp()
        self.checkModServerExists()
        self.conditionalInsertManifest()
        self.checkSelendroidCerts()
        self.checkServerResigned()
        self.conditionalUninstallSelendroid()
        self.conditionalInstallSelendroid()
        self.uninstallApp()
        self.installAppForTest()
        android_common.forwardPort(self.system_port,self.device_port)
        self.pushSelendroid()
        self.waitForServer()
        return self.createSession()

    def stop(self,sessionId):
        data = {}
        data["sessionId"] = sessionId
        body = proxy.execute(Command.QUIT,data)
        print body
        
    def ensureServerExists(self):
        log.debug("Checking whether selendroid is built yet")
        sel_bin = "%s\\matip\\build\\selendroid\\selendroid.apk" % get_python_lib() 
        if os.path.exists(sel_bin):
            self.server_apk = sel_bin
            log.debug("Selendroid server exists")
        else:
            msg = "Selendroid server not exists"
            raise Exception(msg)
    
    def checkInternetPermissionForApp(self):
        has_internet_permission = android_common.hasInternetPermissionFromManifest(self.local_apk)
        if not has_internet_permission:
            msg = """
            apk does not have INTERNET permissions. Selendroid needs internet 
            permission to proceed, please check if you have <uses-permission 
            android:name=\"android.**permission.INTERNET\"/> in your 
            AndroidManifest.xml
            """
            raise Exception(msg)

    def checkModServerExists(self):
        self.mod_app_pkg = self.pkg + ".selendroid"
        try:
            self.mod_server_timestamp = os.stat(self.selendroid_server_path).st_mtime
            self.mod_server_exists =  True
        except:
            pass

    def conditionalInsertManifest(self):
        if not self.mod_server_exists:
            log.debug("Rebuilt selendroid server does not exist, inserting modified manifest")
            self.insertSelendroidManifest(self.server_apk)
        else:
            log.debug("Rebuilt selendroid server already exists, no need to rebuild it with a new manifest")

    def insertSelendroidManifest(self,server_path):
        log.debug("Inserting selendroid manifest")
        new_server_path = self.selendroid_server_path
        new_package = self.pkg + ".selendroid"
        src_manifest = "%s\\matip\\build\\selendroid\\AndroidManifest.xml" % get_python_lib()
        dst_dir = os.path.join(self.temp_dir,self.pkg)
        dst_manifest = os.path.join(dst_dir,"AndroidManifest.xml")

        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        os.mkdir(dst_dir)
        shutil.copyfile(src_manifest,dst_manifest)
        android_common.compileManifest(dst_manifest,new_package,self.pkg)
        android_common.insertManifest(dst_manifest,server_path,new_server_path)

    def checkSelendroidCerts(self):
        apks = [self.selendroid_server_path,self.local_apk]
        for apk in apks:
            log.debug("Checking signed status of %s" % apk)
            android_common.checkAndSignApk(apk)


    def checkServerResigned(self):
        if self.mod_server_exists:
            try:
                timestamp = os.stat(self.selendroid_server_path).st_mtime
                if timestamp > self.mod_server_timestamp:
                    self.mod_server_exists = False
            except:
                pass

    def conditionalUninstallSelendroid(self):
        android_common.uninstallExcessSelendroid(self.pkg)
        installed = android_common.isInstalled(self.mod_app_pkg)
        if not self.mod_server_exists and installed:
            android_common.uninstall(self.mod_app_pkg)    

    def conditionalInstallSelendroid(self):
        installed = android_common.isInstalled(self.mod_app_pkg)
        if not installed:
            log.debug("Rebuilt selendroid is not installed,installing it")
            android_common.install(self.selendroid_server_path)
        else:
            log.debug("Rebuilt selendorid server already exists,no need to rebuild it with a new manifest")

    def uninstallApp(self):
        if self.skip_uninstall:
            log.debug("Not uninstalling app since server not started with --full-reset")
        else:
            installed = android_common.isInstalled(self.pkg)
            if installed:
                android_common.uninstall(self.pkg)

    def installAppForTest(self):
        if not self.local_apk:
            log.debug("Skipping install since we launched with a package instead of an app path")
            return False
        android_common.checkAndSignApk(self.local_apk)
        remote_apk = android_common.remoteApkExists(self.local_apk)
        installed = android_common.isInstalled(self.pkg)
        if installed and remote_apk and self.fast_reset:
            android_common.resetApp(self.fast_reset,self.pkg)
        elif not installed or (self.fast_reset and not remote_apk):
            android_common.mkRemoteDir()
            remote_apk,md5_hash = android_common.getRemoteApk(self.local_apk)
            android_common.removeTempApks([md5_hash])
            android_common.installRemoteWithRetry(remote_apk,self.pkg,self.local_apk)

    def pushSelendroid(self):
        instrument_with = "%s.selendroid/io.selendroid.ServerInstrumentation" % self.pkg
        android_common.instrument(self.pkg,self.activity,instrument_with)    
    
    def waitForServer(self):
        android_common.waitForActivityOn(self.pkg,self.activity)
        wait_sec = 20
        sec = 0.75
        end_at = time.time() + wait_sec
        def pingServer():
            try:
                body = proxy.execute(Command.STATUS,None)
                if body == None or not body:
                    if time.time() < end_at:
                        time.sleep(sec)
                        pingServer()
                    else:
                        msg = "Waited %s secs for selendroid server and it never showed up" % wait_sec
                        raise Exception(msg)
                else:
                    log.debug("Selendroid server is alive!")
            except Exception,ex:
                if time.time() < end_at:
                    time.sleep(sec)
                    pingServer()
                else:
                    msg = "Waited %s secs for selendroid server and it never showed up" % wait_sec
                    raise Exception(msg)
        pingServer()

    def createSession(self):
        log.debug("Creating Selendroid session")
        data = {"desiredCapabilities":self.caps}
        response = proxy.execute(Command.NEW_SESSION,data)
        sessionId = response["sessionId"]
        log.debug("Successfully started selendroid session, session id with: '%s'" % (sessionId))
        return sessionId

