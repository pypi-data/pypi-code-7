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

time_clock_failure = "Fault detected:  Time clock failure."
possible_fault = "Possible fault:  Potential failures - cmd log, comms, or actuator."
likely_fault = "Likely fault:  Potential failures - cmd log, comms, or actuator."
fault_detected = "Fault detected: Failure in comms or actuator."
no_fault_no_failure = "No fault, no failure."
no_fault_failure_in_cmd_log = "No fault, but failure in cmd log."

def type_one_fault_check(schedule, relay_timeseries, override_timeseries, load_timeseries = None, expected_load_min_change = None, expected_load_max_change = None, relay_time_comparison_epsilon = timedelta(minutes=5), override_timeout = timedelta(hours=2), system_time_vs_real_time_timeseries = None):
    """
        Checks the faults caused by a mismatch between schedule, relay state, override and loads.
    """
    from relay_schedule_mismatches import relay_schedule_mismatches, Relay_Status_Point
    from recent_switch_override import recent_switch_override
    from load_analysis import max_load_change_at_time    

    if (not schedule) or (not relay_timeseries) or override_timeseries is None:
        return None    

    desired_load_min_change = abs(expected_load_min_change) if expected_load_min_change else None
    desired_load_max_change = abs(expected_load_max_change) if expected_load_max_change else None     

    relay_mismatches, ok_points = relay_schedule_mismatches(relay_timeseries, schedule, relay_time_comparison_epsilon)

    if not relay_mismatches:
        return None
    
    override_times = None
    override_values = None
    if override_timeseries and len(override_timeseries) > 0:
        override_times, override_values = zip(*override_timeseries)

    no_recent_overrides = []
    recent_overrides = []

    for relay_status_pt in relay_mismatches:        
        recent_override_time, recent_override_value = recent_switch_override(override_times, override_values, relay_status_pt.time, override_timeout)        

        if recent_override_time:
            recent_overrides.append((relay_status_pt, recent_override_time, recent_override_value))
        else:
            no_recent_overrides.append(relay_status_pt)

    load_times = None
    load_values = None
    if load_timeseries != None:
        load_times, load_values = zip(*load_timeseries)

    res = []
    cur_schedule_block = None

    for relay_status_pt in no_recent_overrides:
        if cur_schedule_block is None or cur_schedule_block != relay_status_pt.schedule_block:
            cur_schedule_block = relay_status_pt.schedule_block
            load_change = max_load_change_at_time(load_times, load_values, cur_schedule_block.start_time)          
        
        if load_change != None:
            acceptable_load_change = desired_load_min_change <= load_change <= desired_load_max_change
            if acceptable_load_change:
                res.append((relay_status_pt, no_fault_failure_in_cmd_log))
            else:
                res.append((relay_status_pt, fault_detected))
        else:
            res.append((relay_status_pt, possible_fault))

    cur_schedule_block = None
    for relay_status_pt, override_time, override_value in recent_overrides:
        if override_value != relay_status_pt.value:
            if cur_schedule_block is None or cur_schedule_block != relay_status_pt.schedule_block:
                cur_schedule_block = relay_status_pt.schedule_block
                load_change = max_load_change_at_time(load_times, load_values, cur_schedule_block.start_time)          

            if load_change != None:
                acceptable_load_change = desired_load_min_change <= load_change <= desired_load_max_change
                if acceptable_load_change:
                    res.append((relay_status_pt, no_fault_failure_in_cmd_log))
                else:
                    res.append((relay_status_pt, fault_detected))

            else:
                res.append((relay_status_pt, likely_fault))        


    if system_time_vs_real_time_timeseries:
        for t1, t2 in system_time_vs_real_time_timeseries:
            if t1 != t2:
                res.append((Relay_Status_Point(t1, 0, False, schedule.schedule_block(t1)), time_clock_failure))
    return res

            

def filter_type_one_fault_results(type_one_faults, relay_timeseries):
    """
       type_one_fault_check can return a lot of points.  All most people care about is the fault type and (probably) start and end time (if applicable).  This does the filtering to return such a list
    """
    from Hard_Fault import Hard_Fault

    res = []
   
    if not type_one_faults or len(type_one_faults) == 0:
        return []

    if len(type_one_faults) == 1:
        (relay_status_pt, fault_text) = type_one_faults[0]
        res.append(Hard_Fault(relay_status_pt.time, relay_status_pt.time, fault_text))
        return res

    
    cur_fault_points = [type_one_faults[0]]
    idx = 1
    while idx < len(type_one_faults):        
        
        (cur_fault_relay_pt, cur_fault_txt) = type_one_faults[idx]         
        (last_fault_relay_pt, last_fault_txt) = cur_fault_points[-1]
        
        cur_fault_relay_idx = relay_timeseries.index((cur_fault_relay_pt.time, cur_fault_relay_pt.value))
        last_fault_relay_idx = relay_timeseries.index((last_fault_relay_pt.time, last_fault_relay_pt.value))
        
        if cur_fault_relay_idx != last_fault_relay_idx + 1 or cur_fault_txt != last_fault_txt: #if the next fault relay point is not the next relay point or has different text this is the end of the current fault
            res.append(Hard_Fault(cur_fault_points[0][0].time, cur_fault_points[-1][0].time, last_fault_txt))
            cur_fault_points = [type_one_faults[idx]]
            idx += 1
        else:
            cur_fault_points.append((cur_fault_relay_pt, cur_fault_txt))
            idx += 1
    if len(cur_fault_points) > 0:
        res.append(Hard_Fault(cur_fault_points[0][0].time, cur_fault_points[-1][0].time, last_fault_txt))

    return res