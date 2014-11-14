"""
This file allows the module to be executed with `python todot`.

Python packaging voodoo stolen from
https://github.com/pypa/pip/blob/develop/pip/__main__.py
"""

if __package__ == '':
    import os
    import sys
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

if __name__ == "__main__":
    import todot
    todot.main()