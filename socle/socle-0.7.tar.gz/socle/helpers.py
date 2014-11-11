
from menu import choice

RE_HARDWARE_ADDRESS = "([\da-f]{2}:){5}[\da-f]{2}"

def pick_network_interface(func):
    import os
    import re
    import manuf
    def choice_generator():
        for interface in os.listdir("/sys/class/net"):
            if interface == "lo":
                continue

            hardware_address = open(os.path.join("/sys/class/net", interface, "address")).readline().strip().lower()
            if not re.match(RE_HARDWARE_ADDRESS, hardware_address):
                continue
                
            title = "% 9s %s" % (interface, hardware_address)
                
            if interface.startswith("vboxnet"):
                title += " VirtualBox host-only adapter"
            else:
                title += " " + manuf.get(hardware_address, "Unknown network interface controller")
                if os.path.exists(os.path.join("/sys/class/net", interface, "phy80211")):
                    title += " 802.11 wireless"
            yield title, interface
            
    def wrapped(*args):
        return func(choice(
            choice_generator(),
            "Select network interface",
            "Select network inteface you want to reconfigure"), *args)
        
    return wrapped
    
import os
import re
import stat
import subprocess

RE_BLOCKDEVICE = re.compile("(nand|mmcblk\d+|sd[a-z])$")

def list_block_devices():
    for block_device in os.listdir("/sys/block"):
        if RE_BLOCKDEVICE.match(block_device):
            sector_size = open("/sys/class/block/%s/queue/hw_sector_size" % block_device).read().strip()
            yield block_device, int(sector_size)

def list_partitions():
    for block_device, sector_size in list_block_devices():
        for partition in os.listdir("/sys/class/block/%s" % block_device):
            if not partition.startswith(block_device):
                continue
            sector_count = open("/sys/class/block/%s/size" % partition).read().strip()
            yield "/dev/" + partition, block_device, int(sector_size) * int(sector_count)

def list_mountpoints():
    probed = {}
    for line in open("/proc/mounts").readlines():
        dev, mountpoint, filesystem, flags, i, j = line.split(" ")
        probed[dev] = mountpoint
    for partition, block_device, size in list_partitions():
        yield partition, block_device, size, probed.get(partition, None)

def probe_root_filesystem():
    for partition, block_device, size, mountpoint in list_mountpoints():
        if mountpoint == "/":
            return partition, block_device, size
    raise Exception("Root filesystem not mounted?!")

