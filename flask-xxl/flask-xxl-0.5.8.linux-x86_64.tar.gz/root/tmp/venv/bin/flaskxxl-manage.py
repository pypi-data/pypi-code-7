#!/root/tmp/venv/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'flask-xxl==0.5.8','console_scripts','flaskxxl-manage.py'
__requires__ = 'flask-xxl==0.5.8'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('flask-xxl==0.5.8', 'console_scripts', 'flaskxxl-manage.py')()
    )
