#!c:\opt\python27_amd64\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'CreateCloudMap==0.5.2','console_scripts','create_map'
__requires__ = 'CreateCloudMap==0.5.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('CreateCloudMap==0.5.2', 'console_scripts', 'create_map')()
    )
