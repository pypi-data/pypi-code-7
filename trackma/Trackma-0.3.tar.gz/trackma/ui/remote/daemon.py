#!/usr/bin/python

import asyncore
import socket
import time

class Handler(asyncore.dispatcher_with_send):
    engine_ref = None

    def __init__(self, sock, engine_ref):
        self.engine_ref = engine_ref
        asyncore.dispatcher_with_send.__init__(self, sock)

    def say(self, msg):
        self.send(msg)

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.engine_ref += 1
            self.send("Correct %d" % self.engine_ref)
            time.sleep(3)
            self.engine_ref += 1
            self.send("Correct %d" % self.engine_ref)
            time.sleep(3)
            self.engine_ref += 1
            self.send("Correct %d" % self.engine_ref)
            self.send(data)

class TrackmaDaemon(asyncore.dispatcher):
    clients = []
    engine = 0

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()

        print "Biding to %s:%d..." % (host, port)
        self.bind((host, port))
        print "Listening"
        self.listen(5)
        
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print repr(addr)
            self.clients.append(Handler(sock, self.engine))

server = TrackmaDaemon('localhost', 6969)
asyncore.loop()
