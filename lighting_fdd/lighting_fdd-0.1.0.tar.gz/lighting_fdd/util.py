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

from datetime import datetime, timedelta

class Default_Comparison(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

def csv_to_timeseries(s):
    import csv
    from StringIO import StringIO
    from dateutil.parser import parse

    
    if isinstance(s, basestring):
        s = StringIO(s)
    res = []
    reader = csv.reader(s)
    value_parser = lambda x : x
    float_parser = lambda x : float(x)

    first_row = True
    for row in reader:
        #print row
        ts = row[0].strip()
        v = row[1].strip()

        if first_row:
            try:
                float_parser(v)
                value_parser = float_parser
            except:
                pass
        

        res.append((parse(ts), value_parser(v)))

    return res

def file_to_timeseries(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
        return csv_to_timeseries(lines)



def list_to_timeseries(l, tz):
    from dateutil.parser import parse
    
    first_time = l[0][0]
    
    if isinstance(first_time, float) or isinstance(first_time, int):
        converter = lambda x : datetime.fromtimestamp(x)
        try:
            converter(first_time)
        except:
            converter = lambda x : datetime.fromtimestamp(x/1000.0)
        res = [(converter(x[0]), x[1]) for x in l]
    elif isinstance(first_time, datetime):
        res = l
    else:
        res = [(parse(x[0].strip()), float(x[1].strip())) for x in l]
    return res

def to_timeseries(o, tz):
    from os import path

    
    if not o:
        return None
    
    #print "type(o) = %s" % type(o) 

    if isinstance(o, basestring) and path.isfile(o):
        ts = file_to_timeseries(o)
    elif (isinstance(o, basestring) and not path.isfile(o)) or (type(o) == list and len(o[0]) != 2):
        ts = csv_to_timeseries(o)
    elif type(o) == list and len(o[0]) == 2:
        ts = list_to_timeseries(o, tz)
    else:
        raise ValueError("Unsupported timeseries representation.")

    ts = [(i[0].replace(tzinfo=tz), i[1]) for i in ts]

    return ts

def first_index_before_time_with_value(timestamps, values, desired_timestamp, desired_value):
    from bisect import bisect_right

    ts_idx = bisect_right(timestamps, desired_timestamp)
    if ts_idx:
        for i in reversed(range(ts_idx)):
            if values[i] == desired_value:
                return i
    return None

def to_timezone(s=None):
    import pytz
    import tzlocal
    """ returns a pytz timezone object
    if no tz_name is provided a pytz object representing the OS timezone is returned
    """
    if s != None:
        return pytz.timezone(s)
    else:
        return tzlocal.get_localzone()

def days_in_timeseries(ts):
    if len(ts[0]) == 1:
        res = [t.date() for t in ts]
    elif len(ts[0]) == 2:
        res = [t[0].date() for t in ts]
    res = list(set(res))
    return res

def compress_to_change_of_values(ts):
    if ts is None:
        return None
    
    last_val = ts[0][1]
    res = []
    for pt in ts:
        cur_val = pt[1]
        if cur_val != last_val:
            res.append(pt)
            last_val = cur_val
            
    return res

def max_change_during_time_period(timeseries, values, desired_time, band_of_time = timedelta(minutes=5)):
    """
        Calculates the max change in the range [desired_time -  band_of_time, desired_time + band_of_time].
        That is, it finds the largest and smallest values in the time span and returns the difference.
    """
    from bisect import bisect_right

    if not timeseries:
        return None

    if not band_of_time:
        band_of_time = timedelta(seconds = 0)

    i = bisect_right(timeseries, desired_time - band_of_time)
    largest_value = -1e99
    smallest_value = 1e99
    ct = 0

    while i < len(timeseries) and (timeseries[i] <= (desired_time + band_of_time)):
        cur_value = values[i]
        largest_value = max([largest_value, cur_value])
        smallest_value = min([smallest_value, cur_value])
        ct += 1
        i += 1

    if ct < 2:
        return None

    return largest_value - smallest_value
