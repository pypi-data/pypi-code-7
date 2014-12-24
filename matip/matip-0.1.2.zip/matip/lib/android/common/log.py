import logging,tempfile,time

temp_file = tempfile.gettempdir()
logging.basicConfig(
    filename = "%s\matip_%s.log" % (temp_file,int(time.time())),
    format = "%(levelname)s: %(message)s",
    level = logging.DEBUG
    )


def debug(msg):
    logging.debug(msg)
        
