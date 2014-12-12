# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains ExtendedLog Parser module

Ref:
      http://doc.xarli.net/proftpd-doc/modules/mod_log.html
      http://doc.xarli.net/proftpd-doc/modules/mod_log.html#LogFormat

Example:

      ::ffff:10.121.55.149 UNKNOWN bahamas [29/Nov/2012:12:11:07 +0000] "CWD /carlos" 250 -
      ::ffff:10.121.55.149 UNKNOWN bahamas [29/Nov/2012:12:11:07 +0000] "RNTO /carlos/example.file" 250 0
"""
from pyncomings import parsers

import time

GLOBAL_CWD = ""

class LogFileParser(parsers.LogFileParser):

    def __init__(self, mark_file, jobs=[]):
        super(LogFileParser, self).__init__(mark_file, jobs)
    
    
    def parse_line(self, line):
        """
        Parse a log line.
        """
        global GLOBAL_CWD
        line_items = line.split('"')
        try:
            path = line_items[1].split()[1]
            if line_items[1].split()[0] == "RNTO":
                if path[0] != "/":
                    path = GLOBAL_CWD + "/" + path
                entry = {
                  "entry_id": None,
                  "registration_date": time.time() ,
                  "source": line_items[0].split()[0],
                  "size": line_items[2].split()[1],
                  "status": line_items[2].split()[0],
                  "command": line_items[1].split()[0],
                  "path": path,
                  "user": line_items[0].split()[2],
                  "retention_days": 0,
                  "purged_date": False
                }
                return entry
            if line_items[1].split()[0] == "CWD":
                GLOBAL_CWD = path
            else:
             return None
        except Exception:
          return None



