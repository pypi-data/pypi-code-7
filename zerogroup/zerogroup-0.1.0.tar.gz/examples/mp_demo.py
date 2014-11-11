#!/usr/bin/env python

"""
Farm out processing to multiple processes via zmq.
"""

import re, time, threading
import multiprocessing as mp

import zmq

from zerogroup import ZeroGroup

data = "demo foo bar not baz quux"
s_list = ['demo', 'foo', 'bar', 'quux']

class MyProcess(mp.Process):
    def find_str(self, s, data):
        res = re.search(s, data, re.MULTILINE)
        if res is not None:
            return res.start()

    def run(self):
        g = ZeroGroup()
        g.add(zmq.REP, "tcp://localhost:5555", False,
              {}, 'data', True)
        g.add(zmq.SUB, "tcp://localhost:5556", False,
              {zmq.SUBSCRIBE: ''}, 'ctrl', True)
        g.create()

        # Note that the control socket stream isn't flushed when a quit signal
        # is received because doing so causes errors:
        def ctrl_handler(msg):
            if msg[0] == 'quit':
                g.flush('data')
                g.ioloop.stop()
        g.on_recv('ctrl', ctrl_handler)

        def data_handler(msg):
            s, d = msg
            g.send_multipart('data', [s, str(self.find_str(s, d))])
        g.on_recv('data', data_handler)
        g.start_loop()


if __name__ == '__main__':

    # This must come before the sockets are added to the main parent
    # process:
    p_list = [MyProcess() for i in xrange(2)]
    map(lambda p: p.start(), p_list)

    g = ZeroGroup()
    g.add(zmq.DEALER, "tcp://*:5555", True, {}, 'data')
    g.add(zmq.PUB, "tcp://*:5556", True, {}, 'ctrl')
    g.create()

    # Send data to workers for processing:
    results = []
    for s in s_list:
        g.send_multipart('data', ['', s, data])
    
    # Wait for all results to arrive:
    while len(results) < len(s_list):
        if g.poll('data', 10):
            _, s, d = g.recv_multipart('data')
            results.append((s, d))

    # Send quit signals until all workers stop running:
    while p_list:
        g.send('ctrl', 'quit')
        for p in p_list:
            if not p.is_alive():
                p_list.remove(p)

    # Display results:
    print results
