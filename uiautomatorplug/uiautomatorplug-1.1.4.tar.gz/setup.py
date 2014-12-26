#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = ['uiautomator']

setup(name='uiautomatorplug',
      version='1.1.4',
      description='enhancement for the python wrapper of android uiautomator. provides image comparision method',
      long_description='''\

reference:\n
the python wrapper of android uiautomator:\n
    https://pypi.python.org/pypi/uiautomator/\n

dependency:\n
1: sudo apt-get install python-opencv\n
2: sudo apt-get install python-numpy\n
3: target android device: sdk_version>=16\n

usage:\n
>>> from uiautomatorplug.android import device as d\n
>>> d.info\n
>>> d.orientation\n
>>> d.orientation = 'l'\n
>>> d.wakeup()\n
>>> d.start_activity('--activity-clear-task', action='android.intent.action.DIAL', data='tel:xxxx', flags=0x04000000)\n
>>> d.start_activity('--activity-clear-task', component='com.android.settings/.Settings')
>>> d.find('phone_launch_success.png') \n
>>> d.click(100, 200) \n
>>> d.click('abspath/DPAD_NUMBER_1.png') \n
>>> d.click('abspath/DPAD_NUMBER_1.png', rotation=90) \n
>>> d.exists(text='string_value_of_screen_layout_component_text_attribute') \n
>>> d.expect('abspath/phone_launch_success.png') \n
>>> d(text='Settings').click() \n
''',
      author='bao hongbin',
      author_email='hongbin.bao@gmail.com',
      install_requires=requires,
      packages = ['uiautomatorplug'],
      setup_requires=['uiautomator'],
      license='MIT',
      platforms='any',
      classifiers=(
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Testing',
            )
      )
