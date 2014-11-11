
import os
import subprocess
import tempfile
from helpers import list_mountpoints

def probe(partitions=()):
    if not partitions:
        partitions = [j[0] for j in list_mountpoints()]
        
    for partition in partitions:
        mountpoint = tempfile.mkdtemp()
        cmd = "mount", partition, mountpoint
        subprocess.call(cmd)
        print cmd

        for filename in os.listdir(mountpoint):
            if filename.lower() == "uenv.txt":
                yield partition
                break
            
        cmd = "umount", mountpoint
        subprocess.call(cmd)    
        os.rmdir(mountpoint)

