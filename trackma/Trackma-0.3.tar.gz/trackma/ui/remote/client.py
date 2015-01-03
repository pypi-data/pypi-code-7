#!/usr/bin/python

import time
import socket

s = socket.socket()
host = socket.gethostname()
port = 6969

s.connect((host, port))
time.sleep(2)
print "Sending"
s.sendall("SEND TO YOU")
while True:
    print s.recv(1024)
s.close()
