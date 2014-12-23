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

TIME_CLOCK_FAILURE_MSG = "Fault detected:  Time clock failure."
POSSIBLE_FAULT_MSG = "Possible fault:  Potential failures - cmd log, comms, or actuator."
LIKELY_FAULT_MSG = "Likely fault:  Potential failures - cmd log, comms, or actuator."
FAULT_DETECTED_MSG = "Fault detected: Failure in comms or actuator."
NO_FAULT_NO_FAILURE_MSG = "No fault, no failure."
NO_FAULT_FAILURE_IN_CMD_LOG_MSG = "No fault, but failure in cmd log."

class System_Fault(object):
    def __init__(self, start_time, stop_time, text):
        self.start_time = start_time
        self.stop_time = stop_time
        self.text = text

    def __str__(self):
        return "Fault: %s Start time: %s End time: %s" % (str(self.text), str(self.start_time), str(self.stop_time))

def system_fault_check_verbose(schedule, 
                               relay_timeseries, 
                               override_times, 
                               override_values, 
                               load_times = None, 
                               load_values = None, 
                               expected_load_min_change = None, 
                               expected_load_max_change = None, 
                               relay_time_comparison_epsilon = timedelta(minutes=5), 
                               override_timeout = timedelta(hours=2), 
                               system_time_vs_real_time_timeseries = None):
    """
        Checks the faults caused by a mismatch between schedule, relay state, override and loads.
        Returns every point (with some context) where the relay state does not agree with the scheduled state 
        and there are no acceptable explanations (like a recent override).
        
        Since there are likely to be many it is advisable to filter the results with filter_system_faults.
    """
    from relay_schedule_mismatches import relay_schedule_mismatches, Relay_Status_Point
    from recent_switch_override import recent_switch_override
    from util import max_change_during_time_period    

    if (not schedule) or (not relay_timeseries) or override_times is None:
        return None    

    desired_load_min_change = abs(expected_load_min_change) if expected_load_min_change else None
    desired_load_max_change = abs(expected_load_max_change) if expected_load_max_change else None     

    relay_mismatches, ok_points = relay_schedule_mismatches(relay_timeseries, schedule, relay_time_comparison_epsilon)

    if not relay_mismatches:
        return None

    no_recent_overrides = []
    recent_overrides = []

    for relay_status_pt in relay_mismatches:        
        recent_override_time, recent_override_value = recent_switch_override(override_times, override_values, relay_status_pt.time, override_timeout)        

        if recent_override_time:
            recent_overrides.append((relay_status_pt, recent_override_time, recent_override_value))
        else:
            no_recent_overrides.append(relay_status_pt)

    res = []
    cur_schedule_block = None

    for relay_status_pt in no_recent_overrides:
        if cur_schedule_block is None or cur_schedule_block != relay_status_pt.schedule_block:
            cur_schedule_block = relay_status_pt.schedule_block
            load_change = max_change_during_time_period(load_times, load_values, cur_schedule_block.start_time, relay_time_comparison_epsilon)          
        
        if load_change != None:
            acceptable_load_change = desired_load_min_change <= load_change <= desired_load_max_change
            if acceptable_load_change:
                res.append((relay_status_pt, NO_FAULT_FAILURE_IN_CMD_LOG_MSG))
            else:
                res.append((relay_status_pt, FAULT_DETECTED_MSG))
        else:
            res.append((relay_status_pt, POSSIBLE_FAULT_MSG))

    cur_schedule_block = None
    for relay_status_pt, override_time, override_value in recent_overrides:
        if override_value != relay_status_pt.value:
            if cur_schedule_block is None or cur_schedule_block != relay_status_pt.schedule_block:
                cur_schedule_block = relay_status_pt.schedule_block
                load_change = max_change_during_time_period(load_times, load_values, cur_schedule_block.start_time)          

            if load_change != None:
                acceptable_load_change = desired_load_min_change <= load_change <= desired_load_max_change
                if acceptable_load_change:
                    res.append((relay_status_pt, NO_FAULT_FAILURE_IN_CMD_LOG_MSG))
                else:
                    res.append((relay_status_pt, FAULT_DETECTED_MSG))

            else:
                res.append((relay_status_pt, LIKELY_FAULT_MSG))        


    if system_time_vs_real_time_timeseries:
        for t1, t2 in system_time_vs_real_time_timeseries:
            if t1 != t2:
                res.append((Relay_Status_Point(t1, 0, False, schedule.schedule_block(t1)), TIME_CLOCK_FAILURE_MSG))
    return res

            

def filter_system_faults(system_faults, relay_timeseries):
    """
       system_fault_check can return a lot of points.  All most people care about is the fault type and (probably) start and end time (if applicable).  
       This does the filtering to return such a list.
    """
    res = []
   
    if not system_faults or len(system_faults) == 0:
        return []

    if len(system_faults) == 1:
        (relay_status_pt, fault_text) = system_faults[0]
        res.append(System_Fault(relay_status_pt.time, relay_status_pt.time, fault_text))
        return res

    
    cur_fault_points = [system_faults[0]]
    idx = 1
    while idx < len(system_faults):        
        
        (cur_fault_relay_pt, cur_fault_txt) = system_faults[idx]         
        (last_fault_relay_pt, last_fault_txt) = cur_fault_points[-1]
     
        cur_fault_relay_idx = relay_timeseries.index((cur_fault_relay_pt.time, cur_fault_relay_pt.value))
        last_fault_relay_idx = relay_timeseries.index((last_fault_relay_pt.time, last_fault_relay_pt.value))
        
        if cur_fault_relay_idx != last_fault_relay_idx + 1 or cur_fault_txt != last_fault_txt: #if the next fault relay point is not the next relay point or has different text this is the end of the current fault
            res.append(System_Fault(cur_fault_points[0][0].time, cur_fault_points[-1][0].time, last_fault_txt))
            cur_fault_points = [system_faults[idx]]
            idx += 1
        else:
            cur_fault_points.append((cur_fault_relay_pt, cur_fault_txt))
            idx += 1
    if len(cur_fault_points) > 0:
        res.append(System_Fault(cur_fault_points[0][0].time, cur_fault_points[-1][0].time, last_fault_txt))

    return res

def system_fault_check(schedule, relay_timeseries, override_times, override_values, load_times = None, load_values = None, expected_load_min_change = None, expected_load_max_change = None, relay_time_comparison_epsilon = timedelta(minutes=5), override_timeout = timedelta(hours=2), system_time_vs_real_time_timeseries = None):
    """
        Checks the faults caused by a mismatch between schedule, relay state, override and loads.
        Returns a list of System_Fault objects that characterize the fault type as well as provide a possible start and end time.
    """
    verbose_system_faults = system_fault_check_verbose(schedule, relay_timeseries, override_times, override_values, load_times, load_values, expected_load_min_change, expected_load_max_change, relay_time_comparison_epsilon, override_timeout, system_time_vs_real_time_timeseries)
    cleaned_fault_list = filter_system_faults(verbose_system_faults, relay_timeseries)
    return cleaned_fault_list