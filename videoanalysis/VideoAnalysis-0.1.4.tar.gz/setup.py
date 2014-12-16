#!/usr/bin/env python

from setuptools import setup, find_packages

#
# This package also requires Stephen Helms wormtracker package, but
# that is not available on PyPI, so has to be installed by hand. It
# also requires OpenCV, which in my experience doesn't install well
# (or at all) from pyopencv, so you're on your own for that as well.
#
requirements = [
    'ipython',
    'PIL', 'hashlib', 'numpy', 'IPython',
    'IPython.html', 'IPython.utils.traitlets',
    'PIL', 'hashlib', 'numpy', 'scipy', 'h5py', 'skimage',
    'matplotlib', 'ROIWidgets', 'Avery',
]
install_requirements = [
    'ipython >= 2.2',
    'ipython[notebook] >= 2.2',
    'Pillow', 'hashlib', 'numpy', 'scipy', 'h5py', 'scikit-image',
    'matplotlib', 'ROIWidgets', 'Avery',
]

setup(
    name='VideoAnalysis',
    version='0.1.4',
    description='Widgets for analysis of worm videos',
    author='Leon Avery',
    author_email='lavery3@vcu.edu',
    url='https://pypi.python.org/pypi/VideoAnalysis',
    packages=find_packages(),
    install_requires=install_requirements,
    requires=requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Programming Language :: Python',
        'Topic :: Software Development :: Widget Sets',
    ],
)
