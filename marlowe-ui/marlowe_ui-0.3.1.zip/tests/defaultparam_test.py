import sys
import os
sys.path.insert(0, os.path.join(__file__, '..', '..'))

import nose

from marlowe_ui import defaultparam

def test_initiate():
    c = defaultparam.root_example
    d = defaultparam.root_default
