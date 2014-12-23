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

def compare_s1_points_to_s2_block(s1, s2):
    """
    Returns a list of points where schedule 1 disagress with schedule 2
    """
    from datetime import datetime, timedelta

    #this seems a bit silly but also a small sacrifice to keep the week schedule model without having to bring in other libraries.  Or maybe there is an easier way I just don't see.
    a_monday = datetime.strptime("2014-03-03 00:00:00", "%Y-%m-%d %H:%M:%S")

    mismatches = []
    for k, v in s1.day_schedules.iteritems():
        for i in range(len(v)):
            t = v[0][i]
            value = v[1][i]
            correct_day = a_monday + timedelta(days=k)
            correct_day_and_time = correct_day + timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
            other_block = s2.schedule_block(correct_day_and_time)
            if other_block.value != value:
                mismatches.append((k,t))
    return mismatches

def compare_schedules(s1, s2):
    """
        Returns a list of strings telling at which points the two schedules disagree in terms of what the states of lights should be.
    """
    s1_to_s2 = compare_s1_points_to_s2_block(s1, s2)
    s2_to_s1 = compare_s1_points_to_s2_block(s2, s1)

    datetime_weekdays   = ['Monday', 
              'Tuesday', 
              'Wednesday', 
              'Thursday',  
              'Friday', 
              'Saturday',
              'Sunday']

    res = []
    for (weekday, t) in s1_to_s2:
        res.append("%s disagrees with %s on %s at %s" % (s1.name, s2.name, datetime_weekdays[weekday], str(t)))
    for (weekday, t) in s2_to_s1:
        res.append("%s disagrees with %s on %s at %s" % (s1.name, s2.name, datetime_weekdays[weekday], str(t)))

    return list(set(res))