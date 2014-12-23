#---------------------------------------------------------------------------------------
#Lighting Fault Detection and Energy Quantification (c)2014,
#The Regents of the University of California, through Lawrence Berkeley National
#Laboratory (subject to receipt of any required approvals from the U.S.
#Department of Energy).  All rights reserved.
#
#If you have questions about your rights to use or distribute this software,
#please contact Berkeley Lab's Technology Transfer Department at TTD@lbl.gov
#referring to "Lighting Fault Detection and Energy Quantification (LBNL Ref 2014-173)".
#
#NOTICE:  This software was produced by The Regents of the University of
#California under Contract No. DE-AC02-05CH11231 with the Department of Energy.
#For 5 years from November 25, 2014, the Government is granted for itself and
#others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
#license in this data to reproduce, prepare derivative works, and perform
#publicly and display publicly, by or on behalf of the Government. There is
#provision for the possible extension of the term of this license. Subsequent to
#that period or any extension granted, the Government is granted for itself and
#others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
#license in this data to reproduce, prepare derivative works, distribute copies
#to the public, perform publicly and display publicly, and to permit others to
#do so. The specific term of the license can be identified by inquiry made to
#Lawrence Berkeley National Laboratory or DOE. Neither the United States nor the
#United States Department of Energy, nor any of their employees, makes any
#warranty, express or implied, or assumes any legal liability or responsibility
#for the accuracy, completeness, or usefulness of any data, apparatus, product,
#or process disclosed, or represents that its use would not infringe privately
#owned rights.
#---------------------------------------------------------------------------------------

from util import Default_Comparison

class Schedule_Block(Default_Comparison):
    def __init__(self, start_time, end_time, value):
        self.start_time = start_time
        self.end_time = end_time
        self.value = value

class Week_Schedule(object):
    """
        Represents a schedule as values for a day of the week.  It is continuous and circular and defines the change-of-state points.
        
        The main use is the schedule_block function to query the schedule and get the scheduled timeperiod that a given time belongs to
        and what the scheduled state of the system is at that time.
        
        For example consider a very simple schedule that has only two points:  On at 8:00:00 Monday and off at 18:00:00 Friday.
        If schedule_block is called with a datetime whose weekday and time fall in the range [Monday, 8:00:00, Friday, 18:00:00), 
        For example datetime(2014, 09, 17, 23, 0, 21)  then schedule_block would return a Schedule_Block object with 
        start_time = datetime(2014, 09, 15, 8, 0, 0)
        end_time = datetime(2014, 09, 19, 18, 0, 0)
        value = 1
        
        Likewise if the point passed to schedule_block was datetime(2014, 09, 20, 12, 23, 11) then the result would have
        start_time = datetime(2014, 09, 19, 18, 0, 0)
        end_time = datetime(2014, 09, 22, 8, 0, 0)
        value = 0
                   
    """
    def __init__(self, timeseries, name):
        from collections import defaultdict
        self.name = name
        self.day_schedules = defaultdict(lambda : tuple((list(), list())))
        for t, v in timeseries:
            weekday = t.weekday()
            self.day_schedules[weekday][0].append(t.time())            
            self.day_schedules[weekday][1].append(v)            

    def light_status(self, time):
        from bisect import bisect_right
        day_info = self.day_schedules[time.weekday()]
        
        if day_info:
            day_timestamps = day_info[0]
            i = bisect_right(day_timestamps, time.time())
            if i:
                day_values = day_info[1]
                return day_values[i-1]
        raise ValueError

    def block_start(self, timestamp):
        from datetime import timedelta
        from bisect import bisect_right
        day_info = self.day_schedules[timestamp.weekday()]

        if day_info:
            day_timestamps, day_values = day_info
            i = bisect_right(day_timestamps, timestamp.time())
            if i:
                time = day_timestamps[i-1]
                return timestamp.replace(hour=time.hour, minute=time.minute, second=time.second), day_values[i-1]
            else:                
                #start looking at the end of the previous day
                new_timestamp = (timestamp - timedelta(days=1)).replace(hour=23, minute=59, second=59)
                return self.block_start(new_timestamp)
        else:
            #start looking at the end of the previous day
            new_timestamp = (timestamp - timedelta(days=1)).replace(hour=23, minute=59, second=59)
            return self.block_start(new_timestamp)
    
    def block_end(self, timestamp, recurse = False):
        from datetime import timedelta
        from bisect import bisect_left
        day_info = self.day_schedules[timestamp.weekday()]

        if day_info:
            day_timestamps, day_values = day_info
            i = bisect_left(day_timestamps, timestamp.time())
                
            if i >= len(day_timestamps):
                #start looking at the beginning of the next day
                new_timestamp = (timestamp + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                return self.block_end(new_timestamp, True)
            else:
                time = day_timestamps[i]
                value = day_values[i]

                if (not recurse) and (time == timestamp.time()):
                    if i < len(day_timestamps) - 1:
                        i += 1
                        time = day_timestamps[i]
                        value = day_values[i]
                    else:
                        next_day = timestamp.weekday() + 1
                        timestamp += timedelta(days=1)
                        while True:
                            
                            if next_day > 6:
                                next_day = 0
                            try:
                                next_day_timestamps, next_day_values = self.day_schedules[next_day]
                                time = next_day_timestamps[0]
                                value = next_day_values[0]
                                break
                            except:                                                    
                                timestamp += timedelta(days=1)
                                next_day += 1
                else:
                    pass

                return timestamp.replace(hour=time.hour, minute=time.minute, second=time.second), value
        else:
            #start looking at the beginning of the next day
            new_timestamp = (timestamp + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            return self.block_end(new_timestamp, True)

    def schedule_block(self, time):
        start_time, start_value = self.block_start(time)
        end_time, next_value = self.block_end(time)
        return Schedule_Block(start_time, end_time, start_value)


def schedule_factory(txt, name):
    """
    A factory to ease the creation of schedules.
    
    name is the name of the schedule
    txt must be a csv filename or a csv string
    first column of csv must be the timestamp in "%A %H:%M:%S" form
    second column must be either 0 or 1
    """
    import csv
    from datetime import datetime
    from dateutil.parser import parse
#    import sys
    from StringIO import StringIO
    
    if not txt:
        return None
    
    if isinstance(txt, basestring):
        txt = StringIO(txt)

    reader = csv.reader(txt)
    first_row = True
    week_schedule_parser = lambda x : datetime.strptime(x, "%A %H:%M:%S")
    absolute_schedule_parser = lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    float_value_parser = lambda x : float(x)
    no_value_parser = lambda x : x
    timeseries = []
    parser_type = None
    value_parser_type = no_value_parser
    for row in reader:
        #print "row:\t%s" % str(row)
        ts = row[0].strip()
        value = row[1].strip()
        if first_row:
            try:
                week_schedule_parser(ts)        
                parser_type = week_schedule_parser
            except:
                pass

            try:
                absolute_schedule_parser(ts)        
                parser_type = absolute_schedule_parser
            except:                
                pass

            try:
                float_value_parser(value)
                value_parser_type = float_value_parser
            except:
                pass

        first_row = False

        timeseries.append((parse(ts), value_parser_type(value)))

    if parser_type == week_schedule_parser:
        return Week_Schedule(timeseries, name)
    if parser_type == absolute_schedule_parser:
        raise ValueError("Absolute schedules are currently not implemented.")

    raise ValueError