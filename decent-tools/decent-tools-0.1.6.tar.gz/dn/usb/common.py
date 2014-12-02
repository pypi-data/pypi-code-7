import os
import time
import logging

WAIT_TIMEOUT = 5

def wait_for_driver(device_path):
    threshold = 0
    logging.debug('waiting for driver')
    while True:
        if os.path.exists(device_path):
            try:
                f = os.open(device_path, os.O_NONBLOCK)
                if f > 0:
                    os.close(f)
                    break
            except OSError:
                pass
        time.sleep(0.01)
        threshold = threshold + 1
        if threshold > WAIT_TIMEOUT*100:
            raise IOError('Not accessible: ' + str(device_path))

def test_wait_with_manual_plug():
    '''
    Immediately plug ftdi once running this function
    '''
    try:
        wait_for_driver('/dev/tty.usbserial-A900gwLV')
        return True
    except Exception, e:
        print e
        return False
    