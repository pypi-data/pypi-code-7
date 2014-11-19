__author__ = 'shakyEvil'

from setuptools import setup, find_packages

setup(
    name='shakyEvil_TestModule',
    version='1.0.0',
    url='shakyevil.github.io',
    license='MIT',
    author='shakyEvil',
    author_email='38548792@qq.com',
    description='just a test module',
    classifiers=[
        "Programming Language :: Python",
     ],

     platforms='any',
     keywords='shakyEvil test',
    package=find_packages(exclude=['test']),
     install_requires=[]
 )