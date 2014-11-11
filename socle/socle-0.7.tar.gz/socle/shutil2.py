
import os
import xattr
import uuid
import stat

def which(program, fatal=True):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    if fatal:
        raise RuntimeError("Could not find command: " + program)
    return None

def psaux():
    for pid in os.listdir("/proc"):
        try:
            pid = int(pid)
        except ValueError: # Not a pid
            continue
        s = os.stat("/proc/%d" % pid)
        try:
            exe = os.readlink("/proc/%d/exe" % pid)
        except OSError: # Permission denied
            continue
        cmdline = open("/proc/%d/cmdline" % pid).read()
        cmdline = cmdline.split("\x00")[:-1]
        environment = open("/proc/%d/environ" % pid).read()
        environment = dict([i.split("=", 1) for i in environment.split("\x00")[:-1]])
        yield pid, s.st_uid, s.st_gid, exe, cmdline, environment
