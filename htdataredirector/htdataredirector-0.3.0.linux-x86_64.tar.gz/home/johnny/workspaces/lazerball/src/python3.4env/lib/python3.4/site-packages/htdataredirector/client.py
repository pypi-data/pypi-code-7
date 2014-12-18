import json
import logging
from queue import Queue, Empty, Full
from threading import Thread
import sys

import serial

from .publishers.httppublisher import HttpPublisher
from .units.rfd21733.reader import Reader as SourceReader
from htdataredirector import __version__

class HtDataClient:
    def __init__(self, device_path, logger = None):
        self.device_path = device_path
        self.logger = logger

    def run(self, work_queue):
        self.logger.debug('Hit reader is running')
        try:
            with serial.serial_for_url(self.device_path) as io_dev:
                for hit in SourceReader(io_dev):
                    self.logger.info(json.dumps(hit, sort_keys=True))
                    work_queue.put(hit)
        except serial.serialutil.SerialException as e:
            self.logger.debug(e)
        except KeyboardInterrupt:
            pass

def publish(work_queue, publisher = None, logger = None):
    if not publisher:
        return
    while True:
        data = work_queue.get()
        try:
            response = publisher.publish(data)
            if logger:
                logger.info(response)
            else:
                print(resonse)
        except ConnectionRefusedError as e:
            if logger:
                logger.warn(e.strerror)
            else:
                print(e.strerror)


def runner():
    import argparse
    parser = argparse.ArgumentParser(description='View and publish incoming hits to a target url')
    parser.add_argument('source_path', type=str, help='Path to the input source')
    parser.add_argument('publish_uri', type=str, nargs='?', help='Path to target uri')
    parser.add_argument('--log-level', type=str, help='Log level', default='info')
    # TODO: do something with --verbose
    #parser.add_argument('-v', '--verbose', action='store_true', default='Show all output')
    parser.add_argument('-V', '--version', action='version', version="%(prog)s " + __version__)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)

    level = getattr(logging, args.log_level.upper())
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)

    publisher = None
    if args.publish_uri:
        publisher = HttpPublisher(args.publish_uri)

    reader = HtDataClient(args.source_path,logger=logger)
    work_queue = Queue()

    try:
        threads = [Thread(target=publish, args=(work_queue,publisher,logger,), daemon=True) for i in range(2)]
        threads.insert(0,Thread(target=reader.run, args=(work_queue,),daemon=True))

        for t in threads:
            t.start()

        for t in threads:
            t.join()
    except KeyboardInterrupt:
        sys.exit(0)


