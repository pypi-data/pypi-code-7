import sys, os
from django.conf import settings
from mediastore.mediatypes.video.models import QueueItem


LOCK_FILE = getattr(settings, 'MEDIASTORE_VIDEO_LOCK_FILE', '/tmp/mediastore_video_convert.lock')


def get_epoch():
    import datetime, time
    return time.mktime(datetime.datetime.now().timetuple())


def get_next_item():
    previous = None
    while True:
        current = QueueItem.objects.get_next()
        if current is None:
            break
        if current == previous:
            print "detected endless loop"
            sys.exit(1)
        previous = current
        yield current


def lock(update=False):
    if update == False and os.path.exists(LOCK_FILE):
        print "It seems that there is already a process running " +\
            "which proccesses the video queue. Please check and " +\
            "try again. If you are sure there is no process " +\
            "running, you can delete the " + LOCK_FILE + " file " +\
            "or call the command with the argument 'unlock' again."
        return False
    f = file(LOCK_FILE, 'w')
    f.write(str(get_epoch()))
    f.close()
    return True


def unlock():
    if os.path.exists(LOCK_FILE):
        os.unlink(LOCK_FILE)


def process_queue():
    # if we cannot get the lock, abort
    if not lock():
        return
    try:
        for item in get_next_item():
            item.process()
            lock(update=True)
    finally:
        unlock()


def process_queue_threaded():
    import threading
    thread = threading.Thread(target=process_queue)
    thread.daemon = True
    thread.start()
    return thread


def process_queue_systemprocess():
    import multiprocessing
    process = multiprocessing.Process(target=process_queue)
    process.daemon = True
    process.start()
    return process

