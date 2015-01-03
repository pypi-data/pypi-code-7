import dummymp
import logging

import time
import sys
import pdb
import random

# Just a test function.
def test1():
    time.sleep(1)
    logging.info("Test1: Hi there from logging!")
    num = random.randint(2,7)
    logging.info("Test1: Sleeping for %i secs..." % num)
    time.sleep(num)
    if num > 5:
        logging.info("Test1: Returning the random number %i!" % num)
    logging.info("Test1: Bye bye from logging!")
    if num > 5:
        return num

# Just a test function, with args.
def test2(jellybean):
    logging.info("Test2: Hi there! Magical jelly bean number arg is %i - sleeping for %i!" % (jellybean, jellybean))
    time.sleep(jellybean)

# Just a test function, with kwargs.
def test3(**kwargs):
    if "jellybean" in kwargs:
        jb = kwargs["jellybean"]
    else:
        jb = 1
    
    logging.info("Test3: Hi there! Magical jelly bean number is kwarg %i - sleeping for %i!" % (jb, jb))
    time.sleep(jb)

# Just a test function, with BOTH args and kwargs!
def test4(jellybean, **kwargs):
    if "jellybean2" in kwargs:
        jb = kwargs["jellybean2"]
    else:
        jb = 1
    
    logging.info("Test4: Hi there! Magical jelly bean number is arg %i - but sleeping for kwarg %i!" % (jellybean, jb))
    time.sleep(jb)

def start_callback(completed, running, total_procs):
    logging.info("Main: Starting process (%i running, %i/%i completed)" % (running, completed, total_procs))

def end_callback(completed, running, total_procs):
    logging.info("Main: Process done! (%i running, %i/%i completed)" % (running, completed, total_procs))

# If run directly, run some tests using the test function above.
if __name__ == "__main__":
    # Simple running test
    
    # Prime DummyMP by getting the CPU availability now, rather than
    # later!
    dummymp.getCPUAvail()
    
    # Set max number of processes to 2
    dummymp.set_max_processes(2)
    
    # Set the priority mode to AGGRESSIVE
    dummymp.set_priority_mode(dummymp.DUMMYMP_AGGRESSIVE)
    
    # Set up callbacks
    dummymp.set_start_callback(start_callback)
    dummymp.set_end_callback(end_callback)
    
    # Initialize logging to display INFO logs
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    dummymp.run(test1)
    dummymp.run(test1)
    dummymp.run(test1)
    
    dummymp.process_until_done()
    
    print("Test1 results: %s" % str(dummymp.get_returns()))
    
    if len(dummymp.get_returns().keys()) != 3:
        print("ERROR: Could not get all returns!")
        print("Entering debugger.")
        pdb.set_trace()
        sys.exit(1)
    
    # Run with arguments
    dummymp.run(test2, 5)
    dummymp.run(test3, jellybean = 5)
    dummymp.run(test4, 1, jellybean2 = 5)
    dummymp.process_until_done()
    
    # Configuration reset test - this should clear max_processes
    print("Resetting...")
    dummymp.reset()
    dummymp.run(test1)
    dummymp.run(test1)
    dummymp.run(test1)
    
    dummymp.process_until_done()
    
    # Termination test - this should not run all the way through!
    print("Resetting once more...")
    dummymp.reset()
    dummymp.set_max_processes(1)
    
    dummymp.run(test1)
    dummymp.run(test1)
    dummymp.run(test1)
    
    dummymp.process_process()
    
    time.sleep(2)
    
    dummymp.reset()
    dummymp.process_until_done()
