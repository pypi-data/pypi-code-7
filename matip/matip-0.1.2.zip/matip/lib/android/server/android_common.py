#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,re
import subprocess
import helpers
import zipfile
import shutil
import platform
import tempfile
import hashlib
from matip.lib.android.common import gl
from matip.lib.android.common import adb
from matip.lib.android.common import log
from distutils.sysconfig import get_python_lib


def uninstallExcessSelendroid(pkg_t):
    pkg_list = searchApk()
    if len(pkg_list):
        for pkg in pkg_list:
            pkg_1 = pkg[:-11]
            if pkg_1 == pkg_t:
                continue
            try:
                adb.uninstallApk(pkg)
                adb.uninstallApk(pkg_1)
            except:
                pass

def searchApk():
    api_lv = adb.getApiLevel()
    if api_lv < 15:
        msg = "Api Level should >= 15"
        raise Exception(msg)
    pkg_list = []
    cmd = "pm list packages -3 selendroid"
    stdout = adb.shell(cmd)
    for package in stdout.splitlines():
        if package[-11:] == ".selendroid":
            pkg_list.append(package[8:])
    return pkg_list


def hasInternetPermissionFromManifest(local_apk):
    badging = " ".join([gl.AAPT_CMD,"dump","badging",local_apk])
    log.debug("hasInternetPermissionFromManifest: %s" % badging)
    pipe = subprocess.Popen(badging,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        msg = err
        raise Exception(msg)
    has_internet_permission = re.search(r"uses-permission:'android.permission.INTERNET",out)
    return has_internet_permission


def compileManifest(manifest,manifest_pkg,target_pkg):
    log.debug("Vompiling manifest %s" % manifest)
    platform = helpers.getAndroidPlatform()
    compile_manifest = " ".join([gl.AAPT_CMD,"package -M",manifest,"--rename-manifest-package",
                                manifest_pkg,"--rename-instrumentation-target-package",target_pkg,
                                "-I",os.path.join(platform[1],"android.jar"),"-F",
                                manifest+".apk","-f"])
    log.debug(compile_manifest)
    pipe = subprocess.Popen(compile_manifest,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        msg = err
        raise Exception(msg)


def insertManifest(manifest,srcApk,dstApk):
    log.debug("Inserting manifest,src: %s,dst: %s" % (srcApk,dstApk))
    opts = os.path.dirname(manifest)
    zipfiles = zipfile.ZipFile(manifest+".apk")
    zipfiles.extractall(opts)
    zipfiles.close()

    log.debug("Writing tmp apk %s to %s" % (srcApk,dstApk))
    shutil.copyfile(srcApk,dstApk)
    log.debug("Testing zip archive: %s" % dstApk)
    if not helpers.testZipArchive(dstApk):
        msg = "Zip archive was not found"
        raise Exception(msg)

    if platform.system() is "Windows":
        java = os.path.join(os.environ["JAVA_HOME"],"bin","java.exe")
        move_manifest_cmd = "%s\\matip\\build\\jars\\move_manifest.jar" % get_python_lib()
        move_manifest_cmd = " ".join([java,"-jar",move_manifest_cmd,dstApk,manifest])

        log.debug("Moving manifest with: %s" % move_manifest_cmd)    
        pipe = subprocess.Popen(move_manifest_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = pipe.stdout.read()
        err = pipe.stderr.read()
        if err:
            msg = err
            raise Exception(msg)
        log.debug("Inserted manifest")
    else:
        """
        Insert compiled manifest into /tmp/appPackage.clean.apk
        -j = keep only the file, not the dirs
        -m = move manifest into target apk.
        """
        replace_cmd = "zip -j -m %s %s" % (dstApk,manifest)
        log.debug("Moving manifest with: %s" % replace_cmd)
        pipe = subprocess.Popen(replace_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = pipe.stdout.read()
        err = pipe.stderr.read()
        if err:
            msg = err
            raise Exception(msg)
        log.debug("Inserted manifest")


def checkApkCert(apk):
    if not os.path.exists(apk):
        log.debug("APK doesn't exists: %s" % apk)
        return False
    
    java = os.path.join(os.environ["JAVA_HOME"],"bin","java.exe")
    verify_path = "%s\\matip\\build\\jars\\verify.jar" % get_python_lib()
    resign = " ".join([java,"-jar",verify_path,apk])
    log.debug("Checking app cert for %s: %s" % (apk,resign))
    pipe = subprocess.Popen(resign,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        log.debug("App not signed with debug cert.")
        return False
    log.debug("App already signed")
    zipAlignApk(apk)
    return True


def zipAlignApk(apk):
    log.debug("Zip-aligning %s" % apk)
    aligned_apk = tempfile.mkstemp(suffix=".tmp",prefix="matip")[1]
    align_apk = " ".join([gl.ZIPALIGN_CMD,"-f 4",apk,aligned_apk])
    log.debug("zipAlignApk: %s" % align_apk)
    pipe = subprocess.Popen(align_apk,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        msg = err
        raise Exception(msg)    
    shutil.copyfile(aligned_apk,apk)



def sign(apk):
    signWithDefaultCert(apk)
    zipAlignApk(apk)


def signWithDefaultCert(apk):
    java = os.path.join(os.environ["JAVA_HOME"],"bin","java.exe")
    sign_path = "%s\\matip\\build\\jars\\sign.jar" % get_python_lib()
    resign = " ".join([java,"-jar",sign_path,apk,"--override"])
    log.debug("Resigning apk with: %s" % resign)
    pipe = subprocess.Popen(resign,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = pipe.stdout.read()
    err = pipe.stderr.read()
    if err:
        msg = err
        raise Exception(msg) 


def instrument(pkg,activity,instrument_with):
    if activity[0] != ".":
        pkg = ""
    cmd = "am instrument -e main_activity %s%s %s" % (pkg,activity,instrument_with)
    search_re = re.compile("\.+")
    cmd = search_re.sub(".",cmd)
    stdout = adb.shell(cmd)
    if "Exception" in stdout:
        raise Exception(stdout)

def isInstalled(pkg):
    return adb.isAppInstalled(pkg)

def uninstall(pkg):
    adb.uninstallApk(pkg)

def install(apk):
    adb.installApk(apk)

def checkAndSignApk(apk):
    if not checkApkCert(apk):
        sign(apk)

#for selendroid
def remoteApkExists(apk):
    remote_apk,app_md5_hash = getRemoteApk(apk)
    cmd = "ls %s" % remote_apk
    stdout = adb.shell(cmd)
    if not "No such file" in stdout:
        return stdout.strip()
    else:
        return False

#for matip
def remoteApkIsExists(apk):
    remote_apk,app_md5_hash = getRemotePath(apk)
    cmd = "ls %s" % remote_apk
    stdout = adb.shell(cmd)
    if not "No such file" in stdout:
        return stdout.strip()
    else:
        return False
    
#for matip
def getMd5(apk):
    app_md5_hash = getAppMd5(apk)
    app_md5 = "%s%s%s" % (app_md5_hash[0],app_md5_hash,app_md5_hash[-1])
    return app_md5

#for matip
def startApp(pkg,act):
    return adb.startApp(pkg,act)

#for matip
def getRemotePath(apk):
    app_md5 = getMd5(apk)
    remote_temp_path = remoteTempPath()
    remote_apk = "%s%s.apk" % (remote_temp_path,app_md5)
    return remote_apk,app_md5

def getRemoteApk(apk):
    app_md5_hash = getAppMd5(apk)
    remote_temp_path = remoteTempPath()
    remote_apk = "%s%s.apk" % (remote_temp_path,app_md5_hash)
    return remote_apk,app_md5_hash

def resetApp(fast_reset,pkg,remote_apk=None):
    if fast_reset:
        log.debug("Running fast reset (stop and clear)")
        adb.stopAndClear(pkg)
    else:
        log.debug("Running old fashion reset (reinstall)")
        if not remote_apk:
            msg = "Can't run reset if remote apk doesn't exist"
            raise Exception(msg)
        uninstall(pkg)
        adb.installRemote(remote_apk)

def getAppMd5(strFile):
    file = None
    bRet = False
    str_md5 = ""
    try:
        file = open(strFile,"rb")
        md5 = hashlib.md5()
        str_read = ""
        while True:
            str_read = file.read(8096)
            if not str_read:
                break
            md5.update(str_read)
        bRet = True
        str_md5 = md5.hexdigest()
        log.debug("MD5 for app is: %s" % str_md5)
    except Exception,ex:
        print ex
        bRet = False
    finally:
        if file:
            file.close()
    return str_md5

def remoteTempPath():
    return "/data/local/tmp/"

def mkRemoteDir():
    remote_path = remoteTempPath()
    adb.mkdir(remote_path)

def removeTempApks(except_md5):
    log.debug("Removing any old apks")
    remote_temp_path = remoteTempPath()
    cmd = "ls %s*.apk" % remote_temp_path
    try:
        stdout = adb.shell(cmd)
        if "No such file" in stdout:
            apks = []
        else:
            apks = stdout.split("\n")
    except:
        apks = []
    if len(apks) < 1:
        log.debug("No apks to examine")
        return False
    matching_apk_found = False
    no_md5_matched = True
    for path in apks:
        path = path.strip()
        if path != "":
            no_md5_matched = True
            for md5Hash in except_md5:
                if not md5Hash in path:
                    no_md5_matched = False
            if no_md5_matched:
                adb.shell("rm %s%s" % (remote_temp_path,path))
            else:
                log.debug("Found an apk we want to keep at %s%s" % (remote_temp_path,path))
                matching_apk_found = True
    return matching_apk_found

def installRemoteWithRetry(remote_apk,pkg,local_apk):
    try:
        installed = isInstalled(pkg)
        if installed:
            uninstall(pkg)
        adb.installRemote(remote_apk)
    except:
        removeTempApks([])
        adb.push(local_apk,remote_apk)
        adb.installRemote(remote_apk)

def forwardPort(system_port,device_port):
    adb.forwardPorts(system_port,device_port)

def waitForActivityOn(pkg,act):
    adb.waitForActivity(pkg,act)
