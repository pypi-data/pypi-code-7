#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,re
import platform
import subprocess
import time
import zipfile
import gl
import log
from distutils.sysconfig import get_python_lib

def adb(cmd):
    cmd = cmd.strip()
    if not cmd:
        msg = "You need to pass in a command to adb()"
        raise Exception(msg)
    cmd = "%s %s" % (gl.ADB_CMD,cmd)
    log.debug("executing: %s" % cmd)
    pipe = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err and err.find(" bytes in ") == -1:
        msg = err
        raise Exception(msg)
    else:
        if out.lower().find("error:") == -1:
            return out
        else:
            msg = out
            raise Exception(msg)

def shell(cmd):
    shell_cmd = "shell %s" % cmd
    return adb(shell_cmd)

def isDeviceConnected():
    devices = getConnectedDevices()
    if devices == []:
        msg = "0 device(s) connected"
        raise Exception(msg)
    return devices

def getConnectedDevices():
    log.debug("Getting connected devices...")
    stdout = adb("devices")
    devices = []
    stdout = stdout.split("\n")
    for line in stdout:
        if line.strip() and line.find("List of devices") == -1 and line.find("* daemon") == -1 and line.find("offline") == -1:
            lineinfo = line.split("\t")
            devices.append({"udid":lineinfo[0],"state":lineinfo[1]})
    log.debug("%s device(s) connected" % len(devices))
    return devices
            

def waitForDevice(device_id=None,wait_sec=10):
    restartAdb()
    log.debug("Wait for device to be ready(timeout=%s)" % wait_sec)
    sec = 0.75
    end_at = time.time() + wait_sec

    def doWait():
        if time.time() > end_at:
            msg = "Device did not become ready in %s secs; are sure it's powered on?" % wait_sec
            raise Exception(msg)
        devices = getConnectedDevices()
        if devices == []:
            time.sleep(sec)
            doWait()
        else:
            if not device_id:
                setDeviceId(devices[0]["udid"])
                return devices[0]["udid"]
            else:
                for i in range(len(devices)):
                    if devices[i]["udid"] == device_id:
                        setDeviceId(device_id)
                        return device_id
            time.sleep(sec)
    dev = doWait()
    return checkAdbConnectionIsUp(),dev

def restartAdb():
    gl.ADB_CMD = checkAdbPresent()
    gl.AAPT_CMD = checkAaptPresent()
    gl.ZIPALIGN_CMD = checkZipAlignPresent()
    def restart():
        adb("kill-server")
        adb("start-server")
    i = 0
    for i in range(3):
        try:
            restart()
            break
        except Exception,x:
            if i < 3:
                continue
            else:
                msg = x
                raise Exception(msg)

def checkAdbPresent():
    return checkSdkBinaryPresent("adb")

def checkAaptPresent():
    return checkSdkBinaryPresent("aapt")

def checkZipAlignPresent():
    return checkSdkBinaryPresent("zipalign")

def checkSdkBinaryPresent(binary):
    binary_loc = None
    binary_name = binary
    if platform.system() is "Windows":
        if binary_name == "android":
            binary_name += ".bat"
        else:
            if binary_name[-4:].find(".exe") == -1:
                binary_name += ".exe"
    sdk_root = os.environ.has_key("ANDROID_HOME")
    if sdk_root:
        sdk_root_path = os.environ["ANDROID_HOME"]
        binary_locs = [os.path.join(sdk_root_path,"platform-tools",binary_name),os.path.join(os.environ["ANDROID_HOME"],"tools",binary_name)]
        build_tool_dirs = os.listdir(os.path.join(sdk_root_path,"build-tools"))
        for version_dir in build_tool_dirs:
            binary_locs.append(os.path.join(sdk_root_path,"build-tools",version_dir,binary_name))
        for loc in binary_locs:
            if os.path.exists(loc):
                binary_loc = loc
        if binary_loc == None:
            msg = ("""
            Could not find %s in tools,platform-tools,
            or supported build-tools under %s
            do you have android SDK or build-tools installed into this
            location? Supported build tools are:
            %s
            """ % (binary,sdk_root_path,",".join(build_tool_dirs)))
            raise Exception(msg)
        binary_loc = binary_loc.strip()
        return binary_loc
    else:
        return os.path.join(get_python_lib(),"matip","build","platform-tools",binary_name)


def setDeviceId(device_id):
    gl.ADB_CMD += " -s %s" % device_id

def checkAdbConnectionIsUp():
    stdout = shell("echo 'ready'")
    if stdout.find("ready") == 0:
        return True
    else:
        msg = "ADB ping failed,return: %s" % stdout
        raise Exception(msg)
        
def push(local_path,remote_path):
    cmd = "push %s %s" % (local_path,remote_path)
    adb(cmd)

def pull(remote_path,local_path):
    cmd = "pull %s %s" % (remote_path,local_path)
    adb(cmd)

def mkdir(remote_path):
    cmd = "mkdir -p %s" % remote_path
    shell(cmd)

def rimraf(path):
    shell("rm %s" % path)

def forwardPorts(system_port,device_port):
    cmd = "forward tcp:%s tcp:%s" % (system_port,device_port)
    adb(cmd)
    

def packageAndLaunchActivityFromManifest(local_apk):
    badging = " ".join([gl.AAPT_CMD,"dump","badging",local_apk])
    log.debug("packageAndLaunchActivityFromManifest: %s" % badging)
    pipe = subprocess.Popen(badging,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        msg = err
        raise Exception(msg)
    package = re.search(r"(package: name=(\S)+)",out)
    if package:
        package = package.group()
    else:
        msg = "Get package failed"
        raise Exception(msg)

    if len(package) > 16:
        apk_package = package[15:-1]
    else:
        apk_package = None

    activity = re.search(r"(launchable-activity: name=(\S)+)",out)
    if activity:
        activity = activity.group()
    else:
        msg = "Get activity failed"
        raise Exception(msg)
    if len(activity) > 28:
        apk_activity = activity[27:-1]
    else:
        apk_activity = None
    log.debug("badging package: %s" % apk_package)
    log.debug("badging activity: %s" % apk_activity)
    return apk_package,apk_activity



def getFocusedPackageAndActivity():
    log.debug("Getting focused package and activity");
    package = ""
    activity = ""
    if platform.system() is "Windows":
        cmd = "dumpsys window windows | findstr name="
    else:
        cmd = "dumpsys window windows | grep name="
    search_re = re.compile(r"[a-zA-Z0-9\.]+/.[a-zA-Z0-9\.]+")
    stdout = shell(cmd)
    found_match = search_re.findall(stdout)
    if len(found_match) > 0:
        found_match = found_match[0].split("/")
        package = found_match[0]
        activity = found_match[1]
    return package,activity



def waitForActivity(pkg,act,wait_sec=20):
    if waitForActivityOrNot(pkg,act,False,wait_sec):
        return True


def waitForNotActivity(pkg,act,wait_sec=20):
    if waitForActivityOrNot(pkg,act,True,wait_sec):
        return True


def waitForActivityOrNot(pkg,activity,flag,wait_sec=20):
    if not pkg:
        msg = "Package must not be null"
        raise Exception(msg)
    f = ""
    if flag:f = "not "
    log.debug("Waiting for pkg '%s' and activity '%s' to %sbe focused" % (pkg,activity,f) )
    sec = 0.75
    end_at = time.time() + wait_sec

    if activity.find(pkg) == 0:
        activity_1 = activity[:len(pkg)]
            
    def checkForActivity(found_pkg,found_activity):
        found_act = False
        if found_pkg == pkg:
            for act in activity.split(","):
                act = act.strip()
                if act == found_activity or found_activity.find(act) != -1:
                    found_act = True
        return found_act

    def wait():
        found_pkg,found_activity = getFocusedPackageAndActivity()
        found_act = checkForActivity(found_pkg,found_activity)
        if (not flag and found_act) or (flag and not found_act):
            pass
        elif time.time() < end_at:
            time.sleep(sec)
            wait()
        else:
            if flag:
                verb = "stoped"
            else:
                verb = "started"
            msg = "%s/%s never %s.Current: %s/%s" % (pkg,activity,verb,found_pkg,found_activity)
            raise Exception(msg)
    wait()
    return True

def uninstallApk(pkg):
    log.debug("Uninstalling %s" % pkg)
    forceStop(pkg)
    stdout = adb("uninstall %s" % pkg)
    stdout = stdout.strip()
    if stdout.find("Success") != -1:
        return True
    else:
        print stdout
        msg = "App was not uninstalled,maybe it wasn't on device?"
        raise Exception(msg)

def forceStop(pkg):
    shell("am force-stop %s" % pkg)

def installApk(apk,replace=True):
    cmd = "install "
    if replace:
        cmd += "-r "
    cmd += apk
    stdout = adb(cmd)
    stdout = stdout.strip()
    if stdout.find("Success") != -1:
        return True
    else:
        msg = "App was not installed"
        raise Exception(msg)

def installRemote(remote_apk):
    cmd = "pm install -r %s" % remote_apk
    stdout = shell(cmd)
    if stdout.find("Success") != -1:
        return True
    else:
        msg = "Remote insatall failed:%s" % stdout
        raise Exception(msg)

def clear(pkg):
    shell("pm clear %s" % pkg)

def stopAndClear(pkg):
    forceStop(pkg)
    clear(pkg)

def startApp(pkg,act,retry=True):
    api_lv = getApiLevel()
    if api_lv < 15:
        msg = "Api Level should >= 15"
        raise Exception(msg)
    if not pkg or not act:
        msg = "Parameter 'appPackage' and 'appActivity' is required for lunching application"
        raise Exception(msg)
    cmd = "am start -n %s/%s" % (pkg,act)
        
    try:
        stdout = shell(cmd)
    except Exception,x:
        if retry:
            startApp(pkg,act,False)
        else:
            msg = x
            raise Exception(msg)
    return True

def getApiLevel():
    return shell("getprop ro.build.version.sdk")

def getAppStartTotalTime(pkg,act,retry=True):
    api_lv = getApiLevel()
    if api_lv < 15:
        msg = "Api Level should >= 15"
        raise Exception(msg)
    if not pkg or not act:
        msg = "Parameter 'appPackage' and 'appActivity' is required for lunching application"
        raise Exception(msg)
    cmd = "am start -W %s/%s" % (pkg,act)

    try:
        stdout = shell(cmd)
        total_time_re = re.compile(r"TotalTime:\s?\w+")
        total_time = total_time_re.findall(stdout)
        total_time = total_time[0].split(":")[-1].strip()
    except Exception,x:
        if retry:
            getAppStartTotalTime(pkg,act,False)
        else:
            msg = x
            raise Exception(msg)
    return int(total_time)

def isAppInstalled(pkg):
    installed = False
    log.debug("Getting install status for %s" % pkg)
    api_lv = getApiLevel()
    if api_lv < 15:
        msg = "Api Level should >= 15"
        raise Exception(msg)
    cmd = "pm list packages -3 %s" % pkg
    stdout = shell(cmd)
    for package in stdout.splitlines():
        apk_install_re = re.compile(r"^package:%s$" % pkg)
        if apk_install_re.findall(package):
            installed = True
            break
    result = ""
    if not installed:result = "not "
    log.debug("App is %sinstalled" % result)
    return installed

 
def getFocusedControlTree(temp_file):
    """
    api_lv = getApiLevel()
    if api_lv < 16:
        msg = "Api Level should >= 16"
        raise Exception(msg)
    """
    xml = "/data/local/tmp/uidump.xml"
    #rimraf(xml)
    cmd = "uiautomator dump %s" % xml
    shell(cmd)
    pull(xml,temp_file)
    return "%s\\uidump.xml" % temp_file

def getFocusedControlTreeXml():
    """
    api_lv = getApiLevel()
    if api_lv < 16:
        msg = "Api Level should >= 16"
        raise Exception(msg)
    """
    remote_path = remoteTempPath()
    xml = "%suidump.xml" % remote_path
    cmd = "uiautomator dump %s" % xml
    shell(cmd)
    cmd = "cat %s" % xml
    return shell(cmd)

def mkRemoteDir():
    remote_path = remoteTempPath()
    mkdir(remote_path)

def remoteTempPath():
    return "/data/local/tmp/"

def processExists(process_name):
    if not isValidClass(process_name):
        msg = "Invalid process name: %s" % process_name
        raise Exception(msg)
    if platform.system() is "Windows":
        out = shell("ps | findstr %s$" % process_name)
    else:
        out = shell("ps | grep -w %s" % process_name)
    return out

def isValidClass(class_string):
    return re.search(r"(^[a-zA-Z0-9\./_-]+$)",class_string)

def getPIDsByName(process_name):
    stdout = processExists(process_name)
    if stdout:
        pattern = re.compile(r"\d+")
        result = stdout.split(" ")
        result.remove(result[0])
        return  pattern.findall(" ".join(result))[0]
    else:
        msg = "No matching processes found"
        raise Exception(msg)

def isScreenLocked():
    cmd = "dumpsys window"
    stdout = shell(cmd)
    screen_locked_re = re.compile(r"mShowingLockscreen=\w+")
    screen_locked = screen_locked_re.findall(stdout)
    samsung_note_unlocked_re = re.compile(r"mScreenOnFully=\w+")
    samsung_note_unlocked = samsung_note_unlocked_re.findall(stdout)
    gb_screen_locked_re = re.compile(r"mCurrentFocus.+Keyguard")
    gb_screen_locked = gb_screen_locked_re.findall(stdout)
    if screen_locked:
        if screen_locked[0].split("=")[1] == "false":
            return False
        else:
            return True
    elif gb_screen_locked:
        return True
    elif samsung_note_unlocked:
        if samsung_note_unlocked[0].split("=")[1] == "true":
            return False
        else:
            return True
    else:
        return False

def isSoftKeyboardPresent():
    cmd = "dumpsys input_method"
    stdout = shell(cmd)
    keyboard_shown_re = re.compile(r"mInputShown=\w+")
    keyboard_shown = keyboard_shown_re.findall(stdout)
    if keyboard_shown:
        if keyboard_shown[0].split("=")[1] == "true":
            return True
        else:
            return False
    else:
        return False

def isAirplaneModeOn():
    cmd = "settings get global airplane_mode_on"
    stdout = shell(cmd)
    if int(stdout) == 0:
        return False
    else:
        return True

# on: 1 (to turn on) or 0 (to turn off)
def setAirplaneMode(on):
    cmd = "settings put global airplane_mode_on %s" % on
    shell(cmd)
    broadcaseAirplaneMode(on)

# on: 1 (to turn on) or 0 (to turn off)
def broadcaseAirplaneMode(on):
    if on == 1:
        on = "true"
    else:
        on = "false"
    cmd = "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state %s" % on
    shell(cmd)

def isWifiOn():
    cmd = "settings get global wifi_on"
    stdout = shell(cmd)
    if int(stdout) == 0:
        return False
    else:
        return True

def reboot():
    adb("reboot")

def unlockScreen():
    if isScreenLocked():
        log.debug("Unlocking screen")
        pushUnlock()
        timeout = 10
        end_at = time.time() + timeout
        sec = 0.75
        def unlockAndCheck():
            pkg = "io.matip.unlock"
            activity = ".Unlock"
            startApp(pkg,activity)
            if not isScreenLocked():
                return True
            if end_at > time.time():
                msg = "Screen did not unlock"
                raise Exception(msg)
            else:
                time.sleep(sec)
                unlockAndCheck()
        unlockAndCheck()

def pushUnlock():
    unlock_path = os.path.join(get_python_lib(),"matip","build","unlock_apk","unlock.apk")
    installApk(unlock_path)

def getScreenResolution():
    pattern = re.compile(r"\d+")
    if platform.system() is "Windows":
        cmd = "dumpsys display | findstr PhysicalDisplayInfo"
    else:
        cmd = "dumpsys display | grep PhysicalDisplayInfo"
    out = shell(cmd)
    display = pattern.findall(out)
    return (int(display[0]),int(display[1]))



