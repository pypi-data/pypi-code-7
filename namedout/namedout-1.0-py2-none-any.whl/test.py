import os
import sys
from __init__ import dbg
import __init__ as mo

if __name__ == '__main__':
    dbg(bool(dbg))
    a = 1
    dbg(a, os.__name__, dir(os.path)[0], sys.modules.keys()[0])
    dbg(True)

    def tmp():
        a = 2
        mo.dbg(a, os.__name__, dir(os.path)[0], sys.modules.keys()[0])
        a = 3
        mo.dbg(a)

    tmp()
