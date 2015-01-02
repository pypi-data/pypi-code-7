# -*- coding: utf-8 -*-

"""
write a file atomically
"""

# imports
import os
import shutil
import tempfile

# module globals
__all__ = ['ensure_dir', 'write']

def ensure_dir(directory):
    """ensure a directory exists"""
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise OSError("Not a directory: '{}'".format(directory))
        return directory
    os.makedirs(directory)
    return directory


def write(contents, path):
    """atomically write a file taking advantage of move"""

    path = os.path.abspath(path)
    fd, tmp_path = tempfile.mkstemp()
    os.write(fd, contents)
    os.close(fd)
    ensure_dir(os.path.dirname(path))
    shutil.move(tmp_path, path)
