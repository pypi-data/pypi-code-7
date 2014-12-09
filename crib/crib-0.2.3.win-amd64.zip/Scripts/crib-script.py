#!C:\Anaconda\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'crib==0.2.3','console_scripts','crib'
__requires__ = 'crib==0.2.3'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('crib==0.2.3', 'console_scripts', 'crib')()
    )
