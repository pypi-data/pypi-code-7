#!/usr/bin/env python
#TODO: set up python 2/3 meta class to handle "keys" and such
#TODO: serialization
#TODO: update doc
from sys import version_info as _version_info

if _version_info.major == 3:
    from .._py3 import IACBase 
else:
    from .._py2 import IACBase 


