"""
Implementation using OSX command line tools
to manage FTDIUSBSerialDriver. As kextunload and kextload
requires root privilege, one can use this module with sudo
or change the /etc/sudoers file accordingly:

your_login ALL=(ALL) NOPASSWD: /sbin/kextload, /sbin/kextunload

"""

import subprocess
from dn.usb.common import wait_for_driver
import logging

FTDI_BUNDLE_ID = 'com.FTDI.driver.FTDIUSBSerialDriver'
APPLE_FTDI_BUNDLE_ID = 'com.apple.driver.AppleUSBFTDI'

KEXT_FIND = '/usr/sbin/kextfind'
KEXT_UNLOAD = '/sbin/kextunload'
KEXT_LOAD = '/sbin/kextload'

try_bundle = lambda b: len(subprocess.check_output([KEXT_FIND, '-b', b])) > 0

CURRENT_BUNDLE_ID = (
    FTDI_BUNDLE_ID if try_bundle(FTDI_BUNDLE_ID)
    else (
        APPLE_FTDI_BUNDLE_ID if try_bundle(APPLE_FTDI_BUNDLE_ID) 
        else None
        )
    )

def detach_kernel_driver(serial):
    logging.debug('{} is selected as the corresponding kernel driver'.format(CURRENT_BUNDLE_ID))

    if is_kernel_driver_active(serial):
        if subprocess.call(["sudo", KEXT_UNLOAD, "-b", CURRENT_BUNDLE_ID]) != 0:
            logging.error('Kernel driver not properly detached, proceeding anyways')
            # raise IOError('Kernel driver not properly detached.')
        else:
            logging.info('Kernel driver detached')
    else:
        logging.warning('Kernel driver already detached')

def is_kernel_driver_active(serial):
    loaded = subprocess.check_output([KEXT_FIND, '-loaded', '-b', CURRENT_BUNDLE_ID])
    return len(loaded) > 0

def attach_kernel_driver(path, serial):
    logging.debug('Attaching kernel driver')
    if subprocess.call(["sudo", KEXT_LOAD, "-b", CURRENT_BUNDLE_ID]) != 0:
        logging.warning('Kernel driver not properly attached, proceeding anyways')
    wait_for_driver(path)
    logging.info('Kernel driver attached')
