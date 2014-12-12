# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains XFERLOG Parser module
 
Ref: http://compute.cnr.berkeley.edu/cgi-bin/man-cgi?xferlog+4 
"""


from pyncomings import parsers

import time

class LogFileParser(parsers.LogFileParser):

        
    def __init__(self, mark_file, jobs=[]):
        super(LogFileParser, self).__init__(mark_file, jobs)

 
    def parse_line(self, line):
        """
        Parse a log line.
        """
       
        line_items = line.split()

        entry = {
                  "entry_id": None,
                  "registration_date": time.time() ,
                  "source": line_items[6],
                  "size": line_items[7],
                  "path": line_items[8],
                  "user": line_items[13],
                  "retention_days": 0,
                  "purged_date": False
                }
        return entry
