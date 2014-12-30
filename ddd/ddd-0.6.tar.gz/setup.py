#!/usr/bin/env python
from os.path import dirname
from os.path import abspath
from os.path import join
import os
import sys
import shutil
import glob

from distutils.core import setup
from distutils.sysconfig import get_python_lib

cwd = abspath(dirname(__file__))
PACKAGE_NAME = 'ddd'
EXCLUDE_FROM_PACKAGES = []

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent version are
# still present in site-packages.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, PACKAGE_NAME))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
package_dir = PACKAGE_NAME

for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


# Dynamically calculate the version based on ddd.VERSION.
version = __import__(PACKAGE_NAME).get_version()
data_dir = join(dirname(__file__), 'share')
data_files = [(d.replace(data_dir,'share/ddd'), [join(d, f) for f in files]) for d,folders,files in os.walk(data_dir)]


setup(
    name='ddd',
    version=version,
    url='http://www.tnginformationsystems.com/',
    author='Cochise Ruhulessin',
    author_email='cochise.ruhulessin@gmail.com',
    description="Command-Query Responsibility Separation (CQRS) framework",
    packages=packages,
    package_data=package_data,
    data_files=data_files,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Other Environment',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.4',
        'Topic :: Office/Business',

    ]
)
