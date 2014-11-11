#!/usr/bin/env python

"""
Show how to prevent deadlocking because of traffic asymmetry
by sending null messages for a while after signalling a quit.
"""

import itertools, logging, time
import threading as th
import multiprocessing as mp
import zmq

import zerogroup

PORT_DATA = 6000
PORT_CTRL = 6001

def a_func():
    logger = logging.getLogger('a')

    g = zerogroup.ZeroGroup()
    g.add(zmq.ROUTER, 'tcp://*:%i' % PORT_DATA, True, {}, 'data')
    g.add(zmq.DEALER, 'tcp://localhost:%i' % PORT_CTRL, False, 
          {zmq.IDENTITY: 'a'}, 'ctrl', True)
    g.create()

    def handler(msg):
        if msg[0] == 'quit':
            g.flush('ctrl')
            g.stop_loop()

            handler.running = False
            logger.info('recv ctrl quit')
    handler.running = True
    g.on_recv('ctrl', handler)
    g.start_loop(True)

    c = itertools.count()
    while True:
        data = str(c.next())
        g.send_multipart('data', ['b', data])
        g.send('data', data)
        logger.info('sent data %s' % data)

        _, data = g.recv_multipart('data')
        logger.info('recv data %s' % data)

        # Send null data when exiting to prevent destination node from
        # hanging on recv:
        if not handler.running:
            for i in xrange(5):
                g.send_multipart('data', ['b', 'NULL'])
            break
        
def b_func():
    logger = logging.getLogger('b')

    g = zerogroup.ZeroGroup()
    g.add(zmq.DEALER, 'tcp://localhost:%i' % PORT_DATA, False,
          {zmq.IDENTITY: 'b'}, 'data')
    g.add(zmq.DEALER, 'tcp://localhost:%i' % PORT_CTRL, False,
          {zmq.IDENTITY: 'b'}, 'ctrl', True)
    g.create()

    def handler(msg):
        if msg[0] == 'quit':
            g.flush('ctrl')
            g.stop_loop()
            handler.running = False
            logger.info('recv ctrl quit')
    handler.running = True
    g.on_recv('ctrl', handler)
    g.start_loop(True)

    c = itertools.count()
    while True:
        data = str(c.next())
        g.send('data', data)
        logger.info('sent data %s' % data)
        time.sleep(0.01)

        data = g.recv('data')
        logger.info('recv data %s' % data)

        # Send null data when exiting to prevent destination node from
        # hanging on recv:        
        if not handler.running:
            for i in xrange(5):
                g.send('data', 'NULL')
            break
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s')

    ctx = zmq.Context()
    sock = ctx.socket(zmq.ROUTER)
    sock.bind('tcp://*:%i' % PORT_CTRL)

    a = mp.Process(target=a_func)
    a.start()

    b = mp.Process(target=b_func)
    b.start()

    time.sleep(2)

    for i in ['a', 'b']:
        sock.send_multipart([i, 'quit'])

