# -*- coding: utf-8 -*-

import os
import sys

this_dir = os.path.dirname(__file__)
this_dir = os.path.abspath(this_dir)

test_packages_path = os.path.join(this_dir, '_packages')
sys.path.insert(0, test_packages_path)
test_packages_path = os.path.join(this_dir, '..')
sys.path.insert(0, test_packages_path)

from direg import registries
registries.append(os.path.join(this_dir, '_data', 'registry.py'))


def test_all():
    import one  # that's all it takes. test complete.
