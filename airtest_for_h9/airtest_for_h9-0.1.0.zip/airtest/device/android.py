#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
basic operation for a game(like a user does)
'''

import os
import re
import subprocess
import platform
import time

from airtest import base
from com.dtmilano.android.viewclient import ViewClient 
from com.dtmilano.android.viewclient import adbclient

DEBUG = os.getenv("AIRDEBUG")=="true"
log = base.getLogger('android')

__dir__ = os.path.dirname(os.path.abspath(__file__))



def getMem(serialno, package):
    """
    @description details view: http://my.oschina.net/goskyblue/blog/296798

    @param package(string): android package name
    @return dict: {'VSS', 'RSS', 'PSS'} (unit KB)
    """
    command = 'adb -s %s shell ps' %(serialno)
    output = base.check_output(command)
    ret = {}
    for line in str(output).splitlines():
        if line and line.split()[-1] == package:
            # USER PID PPID VSIZE RSS WCHAN PC NAME
            values = line.split()
            if values[3].isdigit() and values[4].isdigit():
                ret.update(dict(VSS=int(values[3]), RSS=int(values[4])))
            else:
                ret.update(dict(VSS=-1, RSS=-1))
            break
    else:
        log.error("mem get: adb shell ps error")
        return {}
    psscmd = 'adb -s %s shell dumpsys meminfo %s' %(serialno, package)
    memout = base.check_output(psscmd)
    pss = 0
    result = re.search(r'\(Pss\):(\s+\d+)+', memout, re.M)
    if result:
        pss = result.group(1)
    else:
        result = re.search(r'TOTAL\s+(\d+)', memout, re.M)
        if result:
            pss = result.group(1)
    ret.update(dict(PSS=int(pss)))
    return ret


def getCpu(serialno, package):
    '''
    @param package(string): android package name
    @return float: the cpu usage
    '''
    command = 'adb -s %s shell dumpsys cpuinfo' % serialno

    cpu_info = base.check_output(command).splitlines()
    try:
        xym_cpu = filter(lambda x: package in x, cpu_info)[0].split()[0]
        cpu = float(xym_cpu[:-1])
        #log.info("cpu: %.2f" % cpu)
        return cpu
    except IndexError:
        log.error("cpu_info error")
        return 0


# get fps
def get_fps():
    """
    Show Fps.

    Warning:
        The phone should not be in standby mode.

    Args:
        none
    """
    pass


# get temperature
def get_tem(serialno):
    """
    Show cpu and battery temperature.

    Args:
        none

    Return:
        (cpu_tem, batter_tem)
    """
    # get cpu temperature command
    TEMPERATURE_CPU_COMMAND = "adb -s %s shell  cat /sys/class/thermal/thermal_zone0/temp" % serialno
    # get battery temperature command
    TEMPERATURE_BATTERY_COMMAND = "adb -s %s shell cat /sys/class/thermal/thermal_zone1/temp " % serialno
    cpu_temp_data = os.popen(TEMPERATURE_CPU_COMMAND)
    battery_temp_data = os.popen(TEMPERATURE_BATTERY_COMMAND)

    try:
        return (round(float(cpu_temp_data.read().strip('\n'))/1000, 2),
                round(float(battery_temp_data.read().strip('\n'))/1000, 2))
    except:
        return (-1.00, -1.00)


# get upload and download data
def get_dat(serialno, pid):
    RCV_COMMAND = 'adb  -s %s shell cat proc/uid_stat/%s/tcp_rcv' % (serialno, pid)
    SND_COMMAND = 'adb  -s %s shell cat proc/uid_stat/%s/tcp_snd' % (serialno, pid)

    rcv_temp_data = os.popen(RCV_COMMAND)
    snd_temp_data = os.popen(SND_COMMAND)

    try:
        return (round(float(snd_temp_data.read().strip('\n'))/1000, 2),
                round(float(rcv_temp_data.read().strip('\n'))/1000, 2))
    except:
        return (-1.00, -1.00)


# from zope.interface.declarations import implementer
# from airtest import interface

#@implementer(interface.IDevice)
class Device(object):
    def __init__(self, serialno=None):
        self._snapshot_method = 'adb'
        print 'SerialNo:', serialno

        self.adb, self._serialno = ViewClient.connectToDeviceOrExit(verbose=False, serialno=serialno)
        self.adb.setReconnect(True) # this way is more stable

        self.vc = ViewClient(self.adb, serialno, autodump=False)
        self._devinfo = self.getdevinfo()

        print 'ProductBrand:', self._devinfo['product_brand']
        print 'CpuCount: %d' % self._devinfo['cpu_count']
        print 'TotalMem: %d MB' % self._devinfo['mem_total']
        print 'FreeMem: %d MB' % self._devinfo['mem_free']

        try:
            if self.adb.isScreenOn():
                self.adb.wake()
        except:
            pass

        width, height = self.shape()
        width, height = min(width, height), max(width, height)
        self._airtoolbox = '/data/local/tmp/airtoolbox'
        self._init_airtoolbox()
        self._init_adbinput()

    def _init_airtoolbox(self):
        ''' init airtoolbox '''
        serialno = self._serialno
        def sh(*args):
            args = ['adb', '-s', serialno] + list(args)
            return subprocess.check_output(args)

        out = sh('shell','sh','-c', 'test -x {tbox} && {tbox} version'.format(
            tbox=self._airtoolbox))
        out = out.strip()
        print 'AirToolbox: '+out.strip()
        version_file = os.path.join(__dir__, '../binfiles/airtoolbox.version')
        version = open(version_file).read().strip()
        if not out.endswith(version):
            print 'upgrade: airtoolbox (ver %s)...' %(version)
            toolbox = os.path.join(__dir__, '../binfiles/airtoolbox')
            sh('push', toolbox, self._airtoolbox)
            sh('shell', 'chmod', '755', self._airtoolbox)

    def _init_adbinput(self):
        apkfile = os.path.join(__dir__, '../binfiles/adb-keyboard.apk')
        pkgname = 'com.android.adbkeyboard'
        if not self.adb.shell('pm path %s' %(pkgname)).strip():
            print 'Install adbkeyboard.apk input method'
            subprocess.call(['adb', '-s', self._serialno, 'install', '-r', apkfile])

    def snapshot(self, filename):
        ''' save screen snapshot '''
        if self._snapshot_method == 'adb':
            log.debug('start take snapshot(%s)'%(filename))
            pil = self.adb.takeSnapshot(reconnect=True)
            pil.save(filename)
        elif self._snapshot_method == 'screencap':
            tmpname = '/data/local/tmp/airtest-tmp-snapshot.png'
            self.adb.shell('screencap -p '+tmpname)
            os.system(' '.join(('adb', '-s', self._serialno, 'pull', tmpname, filename)))
        else:
            raise RuntimeError("No such snapshot method: [%s]" % self._snapshot_method)


    def touch(self, x, y, eventType=adbclient.DOWN_AND_UP):
        '''
        same as adb -s ${SERIALNO} shell input tap x y
        '''
        if eventType == 'down':
            self.adb.shell('{toolbox} input tapdown {x} {y}'.format(
                toolbox=self._airtoolbox, x=x, y=y))
            log.debug('touch down position %s', (x, y))
        elif eventType == 'up':
            self.adb.shell('{toolbox} input tapup'.format(
                toolbox=self._airtoolbox, x=x, y=y))
            log.debug('touch up position %s', (x, y))
        elif eventType == 'down_and_up':
            log.debug('touch position %s', (x, y))
            self.adb.touch(x, y) 
        else:
            raise RuntimeError('unknown eventType: %s' %(eventType))

    def drag(self, (x0, y0), (x1, y1), duration=0.5):
        '''
        Drap screen
        '''
        self.adb.drag((x0, y0), (x1, y1), duration)

    def shape(self):
        ''' 
        Get screen width and height 
        '''
        width = self.adb.getProperty("display.width")
        height = self.adb.getProperty("display.height")
        return (width, height)

    def _type_raw(self, text):
        #adb shell ime enable com.android.adbkeyboard/.AdbIME
        #adb shell ime set com.android.adbkeyboard/.AdbIME
        #adb shell am broadcast -a ADB_INPUT_TEXT --es msg '你好嗎? Hello?'
        #adb shell ime disable com.android.adbkeyboard/.AdbIME
        adbkeyboard = ['com.android.adbkeyboard/.AdbIME']
        ime = ['adb', '-s', self._serialno, 'shell', 'ime']
        subprocess.call(ime+['enable']+adbkeyboard)
        subprocess.call(ime+['set']+adbkeyboard)
        subprocess.call(['adb', '-s', self._serialno, 'shell', 'am', 'broadcast', '-a', 'ADB_INPUT_TEXT', '--es', 'msg', text])
        subprocess.call(ime+['disable']+adbkeyboard)

    def type(self, text):
        '''
        Input some text

        @param text: string (text want to type)
        '''
        log.debug('type text: %s', repr(text))
        first = True
        for s in text.split('\n'):
            if first:
                first=False
            else:
                self.adb.press('ENTER')
            if not s:
                continue
            self._type_raw(s)

    def keyevent(self, event):
        '''
        Send keyevent by adb

        @param event: string (one of MENU, HOME, BACK)
        '''
        self.adb.shell('input keyevent '+str(event))

    def getMem(self, appname):
        return getMem(self._serialno, appname)

    def getCpu(self, appname):
        return getCpu(self._serialno, appname)/self._devinfo['cpu_count']

    def get_tem(self):
        return get_tem(self._serialno)

    def get_dat(self, pid):
        return get_dat(self._serialno, pid)

    def get_fps(self):
        process = subprocess.Popen('''adb -s %s logcat | find "fps"'''%self._serialno,
                                   stdout=subprocess.PIPE, shell=True)

        # outfd = None
        # if output_file:
        #     outfd = open(output_file, 'w')

        fps_list = []
        data = ""
        while True:
            process.stdout.flush()
            data = process.stdout.readline()

            try:
                fps_list = data.split(":")
                if len(fps_list) == 5:
                    print fps_list[4]
                    # if outfd:
                    #     outfd.write((format + '\n') % tuple(time.time() + fps_list[4]))
                    #     outfd.flush()
            except:
                print "hello world!"

            time.sleep(0.1)

    def set_pid(self, package):
        platform_result = platform.platform()
        WIN_COMMAND = '''adb  -s %s shell cat /data/system/packages.list | find "%s"''' %(self._serialno, package)
        LINUX_COMMAND = '''adb  -s %s shell cat /data/system/packages.list | grep "%s"''' %(self._serialno, package)

        try:
            if "win" in platform_result or "Win" in platform_result:
                win_process = os.popen(WIN_COMMAND)
                pid = win_process.read().split()[1]
                return pid
            else:
                linux_process = os.popen(LINUX_COMMAND)
                pid = linux_process.read().split()[1]
                return pid
        except:
            print "can not get %s pid" % package
            return -1

    def start(self, appname, extra={}):
        '''
        Start a program

        @param extra: dict (defined in air.json)
        '''
        self.adb.shell('am start -S -n '+appname+'/'+extra.get('activity'))

    def stop(self, appname, extra={}):
        '''
        Stop app
        '''
        self.adb.shell('am force-stop '+appname)

    def clear(self, appname, extra={}):
        '''
        Stop app and clear data
        '''
        self.adb.shell('pm clear '+appname)

    def getdevinfo(self):
        # cpu
        output = self.adb.shell('cat /proc/cpuinfo')
        matches = re.compile('processor').findall(output)
        cpu_count = len(matches)
        # mem
        output = self.adb.shell('cat /proc/meminfo')
        match = re.compile('MemTotal:\s*(\d+)\s*kB\s*MemFree:\s*(\d+)', re.IGNORECASE).match(output)
        if match:
            mem_total = int(match.group(1), 10)>>10 # MB
            mem_free = int(match.group(2), 10)>>10
        else:
            mem_total = -1
            mem_free = -1

        # brand = self.adb.getProperty('ro.product.brand')
        return {
            'cpu_count': cpu_count,
            'mem_total': mem_total,
            'mem_free': mem_free,
            'product_brand': self.adb.getProperty('ro.product.brand'),
            'product_model': self.adb.getProperty('ro.product.model')
            }
