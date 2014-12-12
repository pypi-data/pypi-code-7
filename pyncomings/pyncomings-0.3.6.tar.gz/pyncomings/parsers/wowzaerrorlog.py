# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains wowza error log Parser module
 
Ref: http://wowza.com
"""


from pyncomings import parsers

import time

class LogFileParser(parsers.LogFileParser):
    """
>>> f = open("wowza_error_log")
>>> l = f.readline()
>>> l
'WARN\tserver\tcomment\t2014-12-12\t06:01:50\t-\t-\t-\t-\t-\t40.119\t-\t-\t-\t-\t-\t-\t-\t-\tDvrStreamStoreBase.storeChunks[str001/_definst_/MBR_TNT_SD_Audio1_800000.stream/MBR_TNT_SD_Audio1_800000.stream.0] : Skipping chunk. A/V packet times differ by 12774 ms, more than allowed 10000 ms.   aTime=82213197 vTime=82225971\n'
>>> l.split("\t")
['WARN', 'server', 'comment', '2014-12-12', '06:01:50', '-', '-', '-', '-', '-', '40.119', '-', '-', '-', '-', '-', '-', '-', '-', 'DvrStreamStoreBase.storeChunks[str001/_definst_/MBR_TNT_SD_Audio1_800000.stream/MBR_TNT_SD_Audio1_800000.stream.0] : Skipping chunk. A/V packet times differ by 12774 ms, more than allowed 10000 ms.   aTime=82213197 vTime=82225971\n']
>>> l.split("\t")[0]
'WARN'
>>> l.split("\t")[1]
'server'
>>> l.split("\t")[2]
'comment'
>>> l.split("\t")[3]
'2014-12-12'
>>> l.split("\t")[4]
'06:01:50'
>>> l.split("\t")[19]
'DvrStreamStoreBase.storeChunks[str001/_definst_/MBR_TNT_SD_Audio1_800000.stream/MBR_TNT_SD_Audio1_800000.stream.0] : Skipping chunk. A/V packet times differ by 12774 ms, more than allowed 10000 ms.   aTime=82213197 vTime=82225971\n'
    """

    def __init__(self, mark_file, jobs=[]):
        super(LogFileParser, self).__init__(mark_file, jobs)


    def parse_line(self, line):
        """
        Parse a log line.
        """

        line_items = line.split("\t")

        try:
            entry = {
                  "entry_id": None,
                  "registration_date": time.time() ,
                  "source": line_items[1],
                  "size": "",
                  "path": line_items[19],
                  "user": line_items[2],
                  "retention_days": 0,
                  "purged_date": False
                }
        except Exception:
            entry = {
                  "entry_id": None,
                  "registration_date": time.time() ,
                  "source": "",
                  "size": "",
                  "path": "",
                  "user": "",
                  "retention_days": 0,
                  "purged_date": False
            }

        return entry
