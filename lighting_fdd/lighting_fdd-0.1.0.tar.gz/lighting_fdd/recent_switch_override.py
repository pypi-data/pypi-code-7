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

def recent_switch_override(timestamps, values, desired_timestamp, override_timeout):
    """
        Returns the most recent override before the desired_timestamp provided it is within within override_timeout of the desired_timestamp
        Returns the override timestamp and the value, None if there is no override within the override_timeout window
        
        timestamps:  list of datetimes.  Override timseries
        values: list of floats.  Override values corresponding to timestamps
        desired_timestamp: datetime.  The timestamp to try and find the most recent override for
        override_timeout: timedelta.  The length of the override timeout.  To find the actual last override prior to the desired time
                            (and not just the one within the normal timeout) use a really large value for override_timeout
    """
    
    if timestamps is None or len(timestamps) == 0:
        return None, None
    
    closest_previous_override_index = most_recent_override_index(timestamps, desired_timestamp)

    if closest_previous_override_index is None:
        return None, None

    override_timestamp = timestamps[closest_previous_override_index]
    override_value = values[closest_previous_override_index]

    if override_timestamp > desired_timestamp - override_timeout:
        return override_timestamp, override_value
    else:
        return None, None

def most_recent_override_index(timestamps, desired_timestamp):
    """
    Returns the index of the closest timestamp that is <= desired_timestamp.
    """
    from bisect import bisect_right

    idx = bisect_right(timestamps, desired_timestamp)
    
    if idx:
        idx -= 1
        closest_previous_time = timestamps[idx]
        
        if closest_previous_time <= desired_timestamp:
            return idx
            
    return None