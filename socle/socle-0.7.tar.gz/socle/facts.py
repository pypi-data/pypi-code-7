
import re
import subprocess
import platform
import string

TTY = subprocess.check_output("/usr/bin/tty").strip()

# Read uname
OPERATING_SYSTEM, \
HOSTNAME, \
KERNEL_VERSION, \
KERNEL_BUILD, \
ARCH, \
PROCESSOR = platform.uname()


# Determine kernel version
m = re.match("(\d+)\.(\d+)", KERNEL_VERSION)
KERNEL_MAJOR, KERNEL_MINOR = [int(j) for j in m.groups()]

# Determine distribution name, release and codename
LSB_DISTRIBUTION = subprocess.check_output(("/usr/bin/lsb_release", "-i", "-s")).strip()
LSB_RELEASE = subprocess.check_output(("/usr/bin/lsb_release", "-r", "-s")).strip()
LSB_CODENAME = subprocess.check_output(("/usr/bin/lsb_release", "-c", "-s")).strip()

# Determine hardware platform
HARDWARE = None
cpuinfo = open("/proc/cpuinfo").read()
m = re.search(r"Hardware\s*:\s*(.+?)[\n$]", cpuinfo)
if m:
    HARDWARE, = m.groups()

# Determine total memory
meminfo = open('/proc/meminfo').read()
m = re.search(r'MemTotal:\s+(\d+)\s*kB', meminfo)
MEM_TOTAL = int(m.groups()[0])

if __name__ == "__main__":
    for key, value in sorted(locals().items(), key=lambda (k,v):k):
        if key[0] not in string.uppercase:
            continue
        print "%s: %s" % (key, repr(value))
