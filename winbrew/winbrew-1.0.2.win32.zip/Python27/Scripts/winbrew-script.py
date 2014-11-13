#!D:\Tools\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'winbrew==1.0.2','console_scripts','winbrew'
__requires__ = 'winbrew==1.0.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('winbrew==1.0.2', 'console_scripts', 'winbrew')()
    )
