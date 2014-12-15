#!/usr/bin/env python

import subprocess, os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
#from distutils.command.install import uninstall as _uninstall
from distutils.dir_util import copy_tree

#
# Patch the patch in setuputils, which broke the following of symlinks
#
def findall(dir = os.curdir):
    """Find all files under 'dir' and return the list of full filenames
    (relative to 'dir').
    """
    all_files = []
    for base, dirs, files in os.walk(dir, followlinks=True):
        if base==os.curdir or base.startswith(os.curdir+os.sep):
            base = base[2:]
        if base:
            files = [os.path.join(base, f) for f in files]
        all_files.extend(filter(os.path.isfile, files))
    return all_files

import distutils.filelist
distutils.filelist.findall = findall    # fix findall bug in distutils.

js_dir = ''
js_files = ['static/widgets/js/*']
requirements = [
    'ipython',
    'IPython.html', 'IPython.utils.traitlets',
]
install_requirements = [
    'ipython >= 2.2',
    'ipython[notebook] >= 2.2',
]

def post_install(dir, profile='default'):
    if not profile:
        profile = 'default'
    ipython_cmd = [
        'ipython',
        '--profile=' + profile,
        '-c',
        'from IPython import get_ipython; print get_ipython().profile_dir.static_dir'
    ]
    default_static = os.path.join(
        os.path.expanduser('~'), '.ipython', 'profile_default', 'static'
    )
    try:
        static_dir = subprocess.check_output(ipython_cmd).rstrip('\r\n')
    except (subprocess.CalledProcessError, OSError) as e:
        static_dir = default_static
    copy_tree(
        os.path.join('static', 'widgets'),
        os.path.join(static_dir, 'widgets'),
        verbose=1,
    )


class install(_install):
    """Extend setuptools.command.install to copy JS files"""
    user_options = _install.user_options + [
        ('profile=',
         None,
        'Specify the ipython profile into which to install JavaScript files'),
    ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.profile = None

    def finalize_options(self):
        _install.finalize_options(self)

    def run(self, *args, **kwargs):
        _install.run(self, *args, **kwargs)
        self.execute(
            post_install,
            (js_dir, getattr(self, 'profile', 'default')),
            msg='Installing JavaScript files'
        )

setup(
    name='Avery',
    version='0.1.0',
    description='Miscellaneous packages',
    author='Leon Avery',
    author_email='lavery3@vcu.edu',
    url='https://pypi.python.org/pypi/Avery',
    packages=find_packages(exclude='static'),
    install_requires=install_requirements,
    requires=requirements,
    package_data={js_dir: js_files},
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Widget Sets',
    ],
    cmdclass={'install': install},
)
