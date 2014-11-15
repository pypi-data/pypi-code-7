import sys
from time import sleep
from binascii import hexlify

import begin

from . import comms

@begin.start
def install(filepath, address, hex=True):
    """Dumps the contents of filepath into the stream at address."""

    sock = comms.open(address)
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(16)
            if data:
                if hex:
                    to_send = b":" + hexlify(data).upper() + b"\r\n"
                else:
                    to_send = data
                print(repr(to_send))
                sock.send(to_send)
            else:
                sock.send(b"\r\n" + bytes((26,)) + b"\r\n")
                break
    sock.close()
