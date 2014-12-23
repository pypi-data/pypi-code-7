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

from datetime import timedelta
from util import Default_Comparison

class Relay_Status_Point(Default_Comparison):
    """
    A container to hold the time, value, whether the value is changing at the time, and the schedule block the point belongs to
    """
    def __init__(self, time, value, is_value_change_time, schedule_block):
        self.time = time
        self.value = value
        self.is_value_change_time = is_value_change_time
        self.schedule_block = schedule_block

def relay_schedule_mismatches(relay_timeseries, schedule, time_comparison_epsilon = timedelta(minutes=5)):
    """
        Finds all relay times where the status is not the expected schedule status.  
        If time_comparison_epsilon is not none then it also checks times in that band to see if the schedule has changed and if the schedule
        matches the relay at any of those it is not considered an error.
        
        relay_timeseries:  timeseries.  The state of the relay system.  Values must be either 1 (on) or 0 (off)
        schedule:  Schedule object
        time_comparison_epsilon:  timedelta.  The grace period for the scheduled change point.  
    """

    cur_schedule_block = None
    prev_schedule_block = None
    next_schedule_block = None
    
    mismatches = []
    ok_times = []
    last_value = None

    for time, value in relay_timeseries:
        if (not cur_schedule_block) or (time < cur_schedule_block.start_time) or (time >= cur_schedule_block.end_time):
            cur_schedule_block = schedule.schedule_block(time)
            next_schedule_block = None
            prev_schedule_block = None

        mismatch_so_far = value != cur_schedule_block.value

        if (time_comparison_epsilon) and (mismatch_so_far) and (time - time_comparison_epsilon < cur_schedule_block.start_time):
            if prev_schedule_block is None:
                prev_schedule_block = schedule.schedule_block(cur_schedule_block.start_time - timedelta(minutes=1))
            mismatch_so_far = value != prev_schedule_block.value

        if (time_comparison_epsilon) and (mismatch_so_far) and (time + time_comparison_epsilon > cur_schedule_block.end_time):
            if next_schedule_block is None:
                next_schedule_block = schedule.schedule_block(cur_schedule_block.end_time + timedelta(minutes=1))
            mismatch_so_far = value != next_schedule_block.value

        value_changing = False
        if last_value is not None and last_value != value:
            value_changing = True

        if mismatch_so_far:
            mismatches.append(Relay_Status_Point(time, value, value_changing, cur_schedule_block))
        else:
            ok_times.append(Relay_Status_Point(time, value, value_changing, cur_schedule_block))

        last_value = value

    return mismatches, ok_times