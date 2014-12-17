from setuptools import setup

setup(
    name='kf5py',
    py_modules = ['kf5py'],
    version='0.1.8',
    author='Chris Teplovs',
    author_email='dr.chris@problemshift.com',
    url='http://problemshift.github.io/kf5py/',
    license='LICENSE.txt',
    description='Python-based utilities for KF5.',
    install_requires=[
        "requests >= 2.3.0"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
