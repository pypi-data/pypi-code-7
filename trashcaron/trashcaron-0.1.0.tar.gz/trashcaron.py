#!/usr/bin/python3

__author__ = 'eayin'
__version__ = '0.1.0'

from subprocess import Popen, PIPE
from argparse import ArgumentParser, ArgumentTypeError
from collections import defaultdict
from os.path import dirname
import os
import time
import traceback
import logging
import logging.handlers
import sys
import copy
import inspect
import shutil
import errno
import glob

app_name = os.path.splitext(os.path.basename(__file__))[0]


class ColoredConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        myrecord = copy.copy(record)
        levelno = myrecord.levelno
        if(levelno >= 50):  # CRITICAL / FATAL
            color = '\x1b[31m'  # red
        elif(levelno >= 40):  # ERROR
            color = '\x1b[31m'  # red
        elif(levelno >= 30):  # WARNING
            color = '\x1b[33m'  # yellow
        elif(levelno >= 20):  # INFO
            color = '\x1b[32m'  # green
        elif(levelno >= 10):  # DEBUG
            color = '\x1b[35m'  # pink
        else:  # NOTSET and anything else
            color = '\x1b[0m'  # normal
        myrecord.msg = color + str(myrecord.msg) + '\x1b[0m'  # normal
        logging.StreamHandler.emit(self, myrecord)

#### Functions
def logInfo(message):
    func = inspect.currentframe().f_back.f_code
    logger.info("%s:%i  %s" % (func.co_name, func.co_firstlineno, message))

def logError(message):
    func = inspect.currentframe().f_back.f_code
    logger.error("%s:%i  %s" % (func.co_name, func.co_firstlineno, message))

def logWarning(message):
    func = inspect.currentframe().f_back.f_code
    logger.warning("%s:%i  %s" % (func.co_name, func.co_firstlineno, message))

def logDebug(message):
    func = inspect.currentframe().f_back.f_code
    logger.debug("%s:%i  %s" % (func.co_name, func.co_firstlineno, message))

def isNumber(s):
    try:
        float(s)
        return int(s)
    except ValueError:
        raise ArgumentTypeError("%s not an integer" % s)

def fileExists(filePathArgs):
    filePath = list()
    logError(filePath)
    if glob.glob(filePath):
        return filePath  # Returns file(s) in given filePath as list.
    else:
        raise ArgumentTypeError("%s does not exist" % filePath)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            logError("Could not create directory")
            raise

relTrashBinPath = ".trashcaron/trashbin"
relTrashLogPath = ".trashcaron/trashlog"
filesystemList = ["rootfs", "cifs", "vfat", "fuseblk", "ext4", "ext3", "ext2", "tmpfs"]  # Fuseblk == ntfs-3g


class Trashcaron:
    def __init__(self, fileNameList, purgeTime, listTrashSizes):
        self.fileNameList = fileNameList
        self.purgeTime = purgeTime
        self.listTrashSizes = listTrashSizes
        if self.purgeTime:
            self.purgeTime *= 86400

    def duSubprocess(self, trashbinPath):
        try:
            p1 = Popen(["du", "-s", "-h", trashbinPath], stdout=PIPE, stderr=PIPE)
            out, err = p1.communicate()
            out = out.decode('utf-8').split("\t")[0]
            err = err.decode('utf-8')
            print("%s %s %s\n" % (out, trashbinPath, err))
        except IOError as e:
            raise e

    def sizeAllTrashbins(self):
        btrfsRootSubvolList = self.findMpoints()[0]
        mpointsWithoutBtrfsTrashbinList = self.findMpoints()[1]
        btrfsDiffSubvolDict = self.btrfsDiffSubvolDict(btrfsRootSubvolList)
        for trashbinPath in mpointsWithoutBtrfsTrashbinList:
            if os.path.isdir(trashbinPath):
                self.duSubprocess(trashbinPath)
        for key in btrfsDiffSubvolDict:
            rootSubvolAbsTrashBinPath = os.path.join(key, relTrashBinPath)
            if os.path.isdir(rootSubvolAbsTrashBinPath):
                logInfo("%s: Found trashbin: %s" % (key, rootSubvolAbsTrashBinPath))
                self.duSubprocess(rootSubvolAbsTrashBinPath)
            else:
                logDebug("%s: Found no trashbin." % rootSubvolAbsTrashBinPath)
            for btrfsDiffSubvol in btrfsDiffSubvolDict[key][0]:  # key is btrfsRootSubvolPath
                subvolAbsTrashBinPath = os.path.join(key, btrfsDiffSubvol, relTrashBinPath)
                if os.path.isdir(subvolAbsTrashBinPath):
                    self.duSubprocess(subvolAbsTrashBinPath)
                else:
                    logDebug("%s: Found no trashbin." % (btrfsDiffSubvol))

    def mntTrashPath(self, filePath):
        path = os.path.abspath(filePath)
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        currentMPoint = path
        mntTrashBinPath = os.path.join(currentMPoint, relTrashBinPath)
        mntTrashLogPath = os.path.join(currentMPoint, relTrashLogPath)
        currentTstamp = str(int(time.time()))
        mntTrashDirPath = os.path.join(mntTrashBinPath, currentTstamp)
        try:
            mkdir_p(mntTrashDirPath)
            if mkdir_p(mntTrashLogPath):
                logDebug("Created trashcaron directories: %s, %s" % (mntTrashLogPath, mntTrashBinPath))
        except IOError as e:
            logError("Creating trahbin/log folders failed for currentMPoint: %s" % currentMPoint)
            raise e
        return mntTrashDirPath

    def deleteFile(self, fileNameList):
        try:
            for fileName in fileNameList:
                shutil.move(fileName, self.mntTrashPath(fileName))
                logWarning("Moved %s to %s" % (fileName, self.mntTrashPath(fileName)))
        except IOError as e:
            raise e

    def deleteOldFiles(self, subvolAbsTrashBinPath):
        logDebug("subvolAbsTrashPath: %s" % subvolAbsTrashBinPath)
        for baseDir, subDirs, file in os.walk(subvolAbsTrashBinPath):
            for subDir in subDirs:
                currentTstamp = int(time.time())
                subDirAbsPath = os.path.join(baseDir, subDir)
                dirCtime = int(os.path.getctime(subDirAbsPath))
                cTimeSpan = currentTstamp - dirCtime
                if cTimeSpan > self.purgeTime:
                    try:
                        shutil.rmtree(subDirAbsPath)
                        logWarning("Purged %s (age %s days)" % (subDirAbsPath, format(cTimeSpan/86400, '.2f')))
                    except IOError as e:
                        logError("Purging failed for %s" % subDirAbsPath)
                        raise e
                    tstamp = int(time.time())
                    with open(os.path.join(dirname(dirname(subvolAbsTrashBinPath)), relTrashLogPath, "%s.log" % tstamp),
                              "a") as myfile:
                        myfile.write("Purged %s (age %s days)\n" % (subDirAbsPath, format(cTimeSpan/86400, '.2f')))
                else:
                    logDebug("%s not deleted, because cTimeSpan %i < purgeTime %i" % (subDirAbsPath,
                                                                                      cTimeSpan, self.purgeTime))
    def findMpoints(self):
        btrfsRootSubvolList = list()
        mpointsWithoutBtrfsTrashbinList = list()
        for line in open("/proc/mounts", "r"):
            mountLineList = line.split(" ")
            if any(mountLineList[2] in s for s in filesystemList):
                mpointsWithoutBtrfsTrashbinList.append(os.path.join(mountLineList[1], relTrashBinPath))
            elif "btrfs" in mountLineList[2]:
                btrfsRootSubvolList.append(mountLineList[1])
        return (btrfsRootSubvolList, mpointsWithoutBtrfsTrashbinList)

    def btrfsReadonlySubvolList(self, btrfsRootSubvolList):  # btrfsPath is root subvol, thus -o switch is not necessary
        btrfsReadonlySubvolList = defaultdict(list)
        for btrfsPath in btrfsRootSubvolList:
            p1 = Popen(["btrfs", "subvol", "list", "-r", btrfsPath], stdout=PIPE, stderr=PIPE)
            out, err = p1.communicate()
            logDebug("out: %s\nerr: %s" % (out, err))
            splitRows = out.decode('utf-8').split("\n")
            splitRows = filter(None, splitRows)
            for row in splitRows:
                splitLineList = row.split(" ")
                removeSet = set(range(8))
                readonlySubvolNameList = [v for i, v in enumerate(splitLineList) if i not in removeSet]
                readonlySubvolRelPath = " ".join(readonlySubvolNameList)
                btrfsReadonlySubvolList[btrfsPath].append(readonlySubvolRelPath)
        return btrfsReadonlySubvolList

    def btrfsAllSubvolDict(self, btrfsRootSubvolList):
        btrfsAllSubvolDict = defaultdict(list)  # Creates key and appends if not existent or just appends if existent.
        for btrfsPath in btrfsRootSubvolList:  # Processing btrfs' root subvol priorly.
            p1 = Popen(["btrfs", "subvol", "list", btrfsPath], stdout=PIPE, stderr=PIPE)
            out, err = p1.communicate()
            logDebug("out: %s\nerr: %s" % (out, err))
            splitRows = out.decode('utf-8').split("\n")
            splitRows = filter(None, splitRows)
            for row in splitRows:
                splitLineList = row.split(" ")
                if int(splitLineList[6]) == 5:  # Filtering btrfs' root subvol here.(bc no -o switch in subprocess call)
                    continue
                removeSet = set(range(8))  # Use set([1,3,4]) to delete non sequential list elements.
                subvolNameList = [v for i, v in enumerate(splitLineList) if i not in removeSet]
                subvolRelPath = " ".join(subvolNameList)  # Joining splitted subvolName from list to string.
                btrfsAllSubvolDict[btrfsPath].append(subvolRelPath)
        return btrfsAllSubvolDict

    def btrfsDiffSubvolDict(self, btrfsRootSubvolList):
        btrfsReadonlySubvolDict = self.btrfsReadonlySubvolList(btrfsRootSubvolList)
        btrfsAllSubvolDict = self.btrfsAllSubvolDict(btrfsRootSubvolList)
        btrfsDiffSubvolDict = defaultdict(list)
        for key in btrfsAllSubvolDict:
            tmpRwSubvolDiffList = btrfsAllSubvolDict[key]
            if key in btrfsReadonlySubvolDict:
                tmpRwSubvolDiffList = list(set(btrfsAllSubvolDict[key]) - set(btrfsReadonlySubvolDict[key]))
            btrfsDiffSubvolDict[key].append(tmpRwSubvolDiffList)
        logInfo("--------------------------------------\n\t\t\tFound these btrfs readonly subvolumes, which are going"
                " to be ignored")
        for key in btrfsReadonlySubvolDict:
            logInfo("\t\t%s" % key)
            for btrfsRoSubvol in btrfsReadonlySubvolDict[key]:
                logInfo("\t\t%s" % btrfsRoSubvol)
        logInfo("\n\t\t\tand found these btrfs readwrite subvolumes, which are going to be searched for trashbins+:")
        for key in btrfsDiffSubvolDict:
            logInfo("\t\t%s" % key)
            for btrfsDiffSubvol in btrfsDiffSubvolDict[key][0]:
                logInfo("\t\t%s" % btrfsDiffSubvol)
        logInfo("--------------------------------------")
        return btrfsDiffSubvolDict

    def btrfsParseMpoints(self, btrfsRootSubvolList):
        logDebug("btrfsRootSubvolList: %s" % btrfsRootSubvolList)  # btrfsRootSubvolList. E.g.: ["/", "/home"]
        btrfsDiffSubvolDict = self.btrfsDiffSubvolDict(btrfsRootSubvolList)
        for key in btrfsDiffSubvolDict:
            rootSubvolAbsTrashBinPath = os.path.join(key, relTrashBinPath)
            logDebug("rootSubvolAbsTrashPath: %s" % rootSubvolAbsTrashBinPath)
            if os.path.isdir(rootSubvolAbsTrashBinPath):
                logInfo("%s: Found trashbin: %s" % (key, rootSubvolAbsTrashBinPath))
                self.deleteOldFiles(rootSubvolAbsTrashBinPath)
            else:
                logInfo("%s: Found no trashbin." % rootSubvolAbsTrashBinPath)
            for btrfsDiffSubvol in btrfsDiffSubvolDict[key][0]:  # key is btrfsRootSubvolPath
                subvolAbsTrashBinPath = os.path.join(key, btrfsDiffSubvol, relTrashBinPath)
                if os.path.isdir(subvolAbsTrashBinPath):
                    logInfo("%s: Found trashbin: %s" % (btrfsDiffSubvol, subvolAbsTrashBinPath))
                    self.deleteOldFiles(subvolAbsTrashBinPath)
                else:
                    logInfo("%s: Found no trashbin." % (btrfsDiffSubvol))

    def run(self):
        if self.purgeTime:
            logDebug("self.purgeTime: %s" % self.purgeTime)
            btrfsRootSubvolList = self.findMpoints()[0]
            mpointsWithoutBtrfsTrashbinList = self.findMpoints()[1]
            if btrfsRootSubvolList:
                self.btrfsParseMpoints(btrfsRootSubvolList)  # btrfsParseMpoints will initiate deleteOldFiles for btrfs.
            for trashbinPath in mpointsWithoutBtrfsTrashbinList:  # For no btrfs we initiate deleteOldfiles here.
                self.deleteOldFiles(trashbinPath)
        if self.fileNameList:
            self.deleteFile(self.fileNameList)
        if self.listTrashSizes:
            self.sizeAllTrashbins()

#### Initializing Logger
logger = logging.getLogger()
logger.addHandler(ColoredConsoleHandler())
log_syslog_handler = logging.handlers.SysLogHandler('/dev/log')
log_syslog_handler.setFormatter(logging.Formatter(app_name + '[%(process)d] %(message)s'))
logger.addHandler(log_syslog_handler)
logger.info('%s v%s by %s' % (app_name, __version__, __author__))
try:
    parser = ArgumentParser(description="With trashcaron you can delete files to a trashbin and delete old files"
                                        " for all trashbins automatically after a specified amount of time.")
    parser.add_argument('-d', '--delete', nargs="*", help='File/Dir to be deleted')
    parser.add_argument('-l', '--listtrashsizes', action='store_true', help='du for all trashbins', required=False)
    parser.add_argument('-pt', '--purgetime', type=isNumber,
                        help="Purge time for all trashbins in currently mounted filesystems. Time in minutes. Just"
                             " write the number of minutes. Don't append a letter to the number.", required=False)
    parser.add_argument('-v', '--info', action='store_true', help='Log level: info', required=False)
    parser.add_argument('-vv', '--debug', action='store_true', help='Log level: debug', required=False)

    args = parser.parse_args()
    fileNameList = list()
    if args.delete:
        for arg in args.delete:
            if not glob.glob(arg):
                logError("File %s does not exist." % arg)
            fileNameList += glob.glob(arg)  # Makes sure that the file actually exists
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.info:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    trashcaron = Trashcaron(fileNameList, args.purgetime, args.listtrashsizes)
    trashcaron.run()
except SystemExit as e:
    if e.code != 0:
        raise
except:
    logger.error('ERROR {0} {1}'.format(sys.exc_info(), traceback.extract_tb(sys.exc_info()[2])))
    raise
exit(0)

