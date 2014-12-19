#!/user/bin/env python
# -*- coding: utf-8 -*-

import os,time,tempfile
import lxml.etree
from matip.lib.android.common.selendroid import Selendroid
from matip.lib.android.common import adb
from matip.lib.android.common import gl
from matip.lib.android.common.adb_actions import AdbActions
from matip.lib.android.common import device
from matip.lib.android.common.mobileelement import MobileElement
from matip.lib.android.server.matip_server import MatipServer
from matip.lib.android.common.wait import Wait


class MobileDriver():
    """
    Attributes:
    #- platformName eg:Android
    - app
    - device
    - model: native or hybrid
    """
    def __init__(self,desired_capabilities):
        if desired_capabilities is None:
            msg = "Desired Capabilities can't be None"
            raise Exception(msg)
        if not isinstance(desired_capabilities,dict):
            msg = "Desired Capabilities must be a dectionary"
            raise Exception(msg)
        try:
            if not desired_capabilities["app"]:
                raise
        except:
            msg = "app can't be None"
            raise Exception(msg)
            
        try:
            device_name = desired_capabilities["device"]
        except:
            device_name = None
        if device_name:
            adb.waitForDevice(device_id = device_name)
        else:
            device_name = adb.waitForDevice()[1]
            desired_capabilities["device"] = device_name
            
        app = desired_capabilities["app"]
        app = device.configureApp(app)
        desired_capabilities["app"] = app
        pkg,act = adb.packageAndLaunchActivityFromManifest(app)
        desired_capabilities["appPackage"] = pkg
        desired_capabilities["appActivity"] = act
        self.pkg = pkg
        self.act = act
        
        try:
            model = desired_capabilities["model"]
        except:
            model = None

        adb.unlockScreen()
        if model.lower() == "hybrid":
            self._selendroid = Selendroid(desired_capabilities)
        elif model.lower() == "native":
            api_lv = adb.getApiLevel()
            if api_lv < 16:
                msg = "Api Level should >= 16"
                raise Exception(msg)
            self.matip = MatipServer(desired_capabilities)
            self.matip.start()
            self._actions = AdbActions()
            adb.mkRemoteDir()
        else:
            msg = "model supported hybrid or native"
            raise Exception(msg)
            
    @property
    def selendroid(self):
        return self._selendroid
    
    @property
    def actions(self):
        return self._actions

    #@property
    def wait(self,timeout=5,interval=0.5):
        print timeout,interval
        return Wait(self,timeout,interval)

    def find_element(self,**opts):
        """
        find element by opts

        :opts:
         -  index
         -  text
         -  resource_id
         -  class_name
         -  package
         -  content_desc

        :Usage:
            driver.find_element(text="text",index=1)
        """
        if not isinstance(opts,dict):
            msg = "opts must be a dectionary"
            raise Exception(msg)
        elif not opts:
            msg = "opts can't be None"
            raise Exception(msg)

        by_xpath,index = self.generate_xpath(opts)
        return self.execute(by_xpath,index)

    def find_elements(self,**opts):
        """
        find element by opts

        :opts:
         -  index
         -  text
         -  resource_id
         -  class_name
         -  package
         -  content_desc

        :Usage:
            driver.find_element(text="text")
        """
        if not isinstance(opts,dict):
            msg = "opts must be a dectionary"
            raise Exception(msg)
        elif not opts:
            msg = "opts can't be None"
            raise Exception(msg)
        by_xpath,index = self.generate_xpath(opts)
        return self.execute(by_xpath)

    def execute(self,by_xpath,index=None):
        timeout = 15
        end_at = time.time() + timeout
        def find(by_xpath):
            xml_string = self.uidump()
            tree = lxml.etree.fromstring(xml_string)
            result = tree.xpath(by_xpath)
            if not index == None:
                if result != []:
                    res = result[index]
                    return MobileElement(res)
                else:
                    return MobileElement(result)
            else:
                res = []
                for i in range(len(result)):
                    elem = result[i]
                    res.append(MobileElement(elem))
                return res
        return find(by_xpath)      

    def generate_xpath(self,opts):
        flag = False
        by_xpath = "//node"
        index = 0
        if len(opts) == 1 and opts.keys()[0] == "index":
            index = int(opts["index"])
        else:
            by_xpath = "//node["
            for opt in opts.iteritems():
                key,what = opt
                how = gl.FINDERS.get(key)
                if how:
                    if how == "index":
                        index = int(what)
                        continue
                    else:
                        if flag:
                            by_xpath += " and "
                        by_xpath += "@%s='%s'" % (how,what)
                        flag = True
                else:
                    msg = "Invalid locator values passed in"
                    raise Exception(msg)
            by_xpath += "]"
        return by_xpath,index

    def uidump(self):
        """
        Get the control tree of the current page
        """
        return adb.getFocusedControlTreeXml()

    def screenshot(self,local_file):
        png = "/data/local/tmp/screenshot.png"
        cmd = "/system/bin/rm %s; /system/bin/screencap -p %s " % (png,png)
        adb.shell(cmd)
        if os.path.exists(local_file):
            os.remove(local_file)
        adb.pull(png,local_file)

    def isSoftKeyboardPresent(self):
        return adb.isSoftKeyboardPresent()

    def isAirplaneModeOn(self):
        return adb.isAirplaneModeOn()

    def isWifiOn(self):
        return adb.isWifiOn()

    def size(self):
        return adb.getScreenResolution()

    def clear(self):
        adb.clear(self.pkg)
    
    
    def quit(self):
        """
        Quits the driver and close app

        :Usage:
            driver.quit()
        """
        try:
            adb.forceStop(self.pkg)
        except:
            pass
