from os import path
import os
import shutil
import sys


def _local_path(name):
    return path.join(path.dirname(__file__), name)


def install_headers(package_name, include_dir=None):
    """Install the headers of a known package_name into include_dir. Known
    package names are ['murmurhash', 'numpy'].

    include_dir defaults to path.join(sys.prefix, 'include'):

    >>> install_headers('numpy')
    >>> assert path.exists(path.join(sys.prefix, 'include', 'numpy', 'ndarray.h'))

    If path.join(include_dir, package_name) exists, install_headers will look
    for any headers that are missing, and add them.
    """
    if include_dir is None:
        include_dir = path.join(sys.prefix, 'include')
    assert path.exists(include_dir) and path.isdir(include_dir)
    src_dir = _local_path(package_name)
    dest_dir = path.join(include_dir, package_name)
    if path.exists(dest_dir):
        for filename in os.listdir(src_dir):
            shutil.copy(path.join(src_dir, filename), path.join(dest_dir, filename))
    else:
        shutil.copytree(src_dir, dest_dir)
