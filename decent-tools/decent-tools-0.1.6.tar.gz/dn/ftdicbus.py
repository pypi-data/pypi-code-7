#!/usr/bin/env python
"""
Sets FTDI CBUS bits using the bit-banging mode.
CBUS is used to select active target connected
FTDI serial interface. Following modes are defined:
    MSP430_UART_MODE    = 0x30
    MSP430_BSL_MODE     = 0x31
    TC65I_MODE          = 0x32
"""

import sys
import argparse
import sys
import ftdi
import usb
import re
import functools
import logging

logger = logging.getLogger(__name__)

MSP430_UART_MODE    = 0x30
MSP430_BSL_MODE     = 0x31
TC65I_MODE          = 0x32

FTDI_VENDOR         = 0x0403
FTDI_PRODUCT        = 0x6001

def extract_serial(device):
    m = re.match('^.*tty.usbserial-(.*)$', device)
    if m:
        serial = m.group(1)
    else:
        serial = None
        logger.warn("Serial number is not recognized %s", device)
    return serial

def ftdi_operation():
    def _wrapper(operation):
        def _actual(*args, **kwargs):
            device = args[0]
            serial = extract_serial(device)
            usb.detach_kernel_driver(serial)
            try:
                ftdic = ftdi.ftdi_new()
                if not ftdic:
                    raise IOError("Cannot allocate ftdi context")
                try:
                    usb_desc = (
                        ftdi.ftdi_usb_open_desc(
                            ftdic, FTDI_VENDOR, FTDI_PRODUCT, 
                            None, serial) if serial
                        else 
                        ftdi.ftdi_usb_open(
                            ftdic, FTDI_VENDOR, FTDI_PRODUCT)
                        )
                    if usb_desc < 0:
                        raise IOError(usb_desc, "Can't open ftdi device")
                    try:
                        #Actual operation
                        kwargs['ftdic'] = ftdic
                        operation(*args, **kwargs)
                    finally:
                        ftdi.ftdi_usb_close(ftdic)
                finally:
                    ftdi.ftdi_free(ftdic)
            finally:
                usb.attach_kernel_driver(device, serial)
        return functools.wraps(operation)(_actual)
    return _wrapper

@ftdi_operation()
def set_cbus_pins(device, mode, ftdic=None):
    ftdi.ftdi_set_bitmode(ftdic, mode, ftdi.BITMODE_CBUS)
    logger.info("ftdi cbus pins changed to: {0:#x}".format(mode))

@ftdi_operation()
def get_cbus_pins(device, ftdic=None):
    pins = ftdi.new_ucharp()
    val = ftdi.ftdi_read_pins(ftdic, pins)
    res = ftdi.ucharp_value(val)
    logger.debug("ftdi cbus pins read: {0:#x}".format(res))

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    choices = {'msp430-uart': MSP430_UART_MODE, 'msp430-bsl': MSP430_BSL_MODE, 'tc65i': TC65I_MODE}
    group.add_argument('-m', '--mode', metavar='MODE',  
        choices=choices.keys(), 
        help='set predefined mode ({})'.format(', '.join(choices.keys())))
    group.add_argument('-s', '--set', metavar='VALUE', help='set raw value in 0xHH format')
    group.add_argument('-r', '--read', action='store_true', help='print raw value in 0xHH format')
    parser.add_argument('-p', '--port', metavar='PATH', help='serial device path', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')
    parser.add_argument(
        '-t', '--attach-timeout', metavar='SECONDS', 
        help='''timeout until device node appears after attaching kernel 
                driver (default is %.1f sec)''' % usb.common.WAIT_TIMEOUT)
    args = parser.parse_args()

    root_logger = logging.getLogger('')
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.ERROR)
    
    if args.verbose:
        root_logger.setLevel(logging.INFO)

    if args.debug:
        root_logger.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('[%(filename)s:%(lineno)d] %(message)s'))
    
    if args.attach_timeout:
        usb.common.WAIT_TIMEOUT = float(args.attach_timeout)

    if args.mode:
        set_cbus_pins(args.port, choices[args.mode])
    elif args.set:
        set_cbus_pins(args.port, int(args.set, 16))
    elif args.read:
        print get_cbus_pins(args.port)

if __name__ == '__main__':
    main()