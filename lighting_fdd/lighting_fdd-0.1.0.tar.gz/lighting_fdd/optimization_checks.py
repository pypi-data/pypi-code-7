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

REDUCE_SCHEDULED_ON_MSG = "Potential to improve efficiency by reducing scheduled hours-on."
EXTEND_SCHEDULED_ON_MSG = "Potential to improve service by extending scheduled hours-on."
REDUCE_OVERRIDE_TIMEOUT_MSG = "Potential to improve efficiency by reducing the length of the override time-out."
EXTEND_OVERRIDE_TIMEOUT_MSG = "Potential to improve service by increasing the length of the override time-out."

def check_total_off_times_for_days_of_week(schedule):
    """
    Checks to see if  "duration of scheduled off time < 8 hours on weekdays or < 12 hours on weekends."  If so reports a potential improvement.

    """
    from datetime import datetime, time
    
    total_on_times = {}
    total_off_times = {}
    tmp_time = datetime.now()
    for i in range(7):
        total_on_time = timedelta(seconds=0)
        total_off_time = timedelta(seconds=0)
        if i in schedule.day_schedules:
            day_times, day_values = schedule.day_schedules[i]

            day_times = [tmp_time.replace(hour=x.hour, minute=x.minute, second=x.second, microsecond=x.microsecond) for x in day_times]
            start_idx = 0
            if day_times[0] == time(hour=0, minute=0):
                if day_values[0] == 0:
                    total_off_time += day_times[1] - day_times[0] - timedelta(seconds=1)
                else:
                    total_on_time += day_times[1] - day_times[0] - timedelta(seconds=1)

                start_idx = 1

            else:
                if i == 0:
                    previous_day = 6
                else:
                    previous_day = i-1
                previous_times, previous_values = schedule.day_schedules[previous_day]                
                previous_value = previous_values[-1]
                if previous_value == 0:
                    total_off_time += day_times[0] - day_times[0].replace(hour=0, minute=0, second=0) - timedelta(seconds=1)
                else:
                    total_on_time += day_times[0] - day_times[0].replace(hour=0, minute=0, second=0) - timedelta(seconds=1)
            
            for day_idx in range(start_idx, len(day_times)-1):
                value = day_values[day_idx]

                if value == 0:
                    total_off_time += day_times[day_idx + 1] - day_times[day_idx] - timedelta(seconds=1)
                else:
                    total_on_time += day_times[day_idx + 1] - day_times[day_idx] - timedelta(seconds=1)

            last_value = day_values[-1]
            if last_value == 0:
                total_off_time += day_times[-1].replace(hour=23, minute=59, second=59) - day_times[-1] - timedelta(seconds=1)
            else:
                total_on_time += day_times[-1].replace(hour=23, minute=59, second=59) - day_times[-1] - timedelta(seconds=1)

        total_on_times[i] = total_on_time
        total_off_times[i] = total_off_time

    res = []
    #first check weekends.  criteria is duration of scheduled off times on weekends < 12 hours?
    for i in range(5,7):    #5 and 6 are Saturday and Sunday
        if total_off_times[i] < timedelta(hours=12):
            res.append((i, REDUCE_SCHEDULED_ON_MSG))

    #now weekdays.  criteria is duration of scheduled off times on weekends < 8 hours?
    for i in range(5):
        if total_off_times[i] < timedelta(hours=8):
            res.append((i, REDUCE_SCHEDULED_ON_MSG))
    return res

def check_switch_events_with_schedule_per_day(schedule, 
                                      override_times,
                                      override_values, 
                                      total_number_of_days, 
                                      frequency_percent = .5, 
                                      after_schedule_time_min = timedelta(hours=1), 
                                      after_scheduled_time_max = timedelta(hours=4), 
                                      prior_to_scheduled_time_min = timedelta(hours=1), 
                                      prior_to_scheduled_max = timedelta(hours=2)):
    """
        Checks the "Do switch events occur frequently and soon before/after scheduled times.
        Faults exist if the happen for more than frequency_percent * total_number_of_days days
        
        schedule:  Schedule object
        override_times:  list of datetimes  
        override_values:  list of floats
        frequency_percent:  float in [0,1].  cutoff for what percent of days must contain a fault for it to be reported 
        after_schedule_time_min:  timedelta.  This with after_scheduled_time_max sets a bounding box for when switch events after a scheduled change should be considered 
        after_scheduled_time_max: timedelta 
        prior_to_scheduled_time_min: timedelta. This along with prior_to_schedule_max sets a bounding box for when switch events before a scheduled change should be considered
        prior_to_scheduled_max: timedelta
                                      
    """

    if not override_times:
        return []
    
    switched_to_off_before_lights_off = 0
    switched_to_on_before_lights_on = 0
    switched_to_on_after_lights_off = 0

    had_switched_to_off_before_lights_off = False
    had_switched_to_on_before_lights_on = False
    had_switched_to_on_after_lights_off = False

    cur_day = None    
    for i in range(len(override_times)):
        cur_time = override_times[i]
        cur_value = override_values[i]

        if not cur_day or cur_time.date() != cur_day:
            had_switched_to_off_before_lights_off = False
            had_switched_to_on_before_lights_on = False
            had_switched_to_on_after_lights_off = False

            cur_day = cur_time.date()


        cur_schedule_block = schedule.schedule_block(cur_time)

        if cur_value == 1: #override to on
            if cur_schedule_block.value == 0:  #but the schedule says it should be off, investigate
                
                if after_schedule_time_min <= cur_time - cur_schedule_block.start_time <= after_scheduled_time_max:  #see if this is being turned on after a scheduled off time
                    if not had_switched_to_on_after_lights_off:
                        switched_to_on_after_lights_off += 1
                        had_switched_to_on_after_lights_off = True

                else: #next check to see if it is being turned on before a scheduled on time
                    next_schedule_block = schedule.schedule_block(cur_schedule_block.end_time + timedelta(seconds=1))

                    if next_schedule_block.value == 1: #next block is an on block
                        if prior_to_scheduled_time_min <= cur_schedule_block.end_time - cur_time <= prior_to_scheduled_max:
                            if not had_switched_to_on_before_lights_on:
                                switched_to_on_before_lights_on += 1
                                had_switched_to_on_before_lights_on = True
            
        else: #override to off
            next_schedule_block = schedule.schedule_block(cur_schedule_block.end_time + timedelta(seconds=1))
            if next_schedule_block.value == 0:    #the next time would be off anyway so investigate
                if prior_to_scheduled_time_min <= cur_schedule_block.end_time - cur_time <= prior_to_scheduled_max:
                    if not had_switched_to_off_before_lights_off:
                        switched_to_off_before_lights_off += 1
                        had_switched_to_off_before_lights_off = True
    
    warnings = []
    cutoff = total_number_of_days * frequency_percent
    if switched_to_off_before_lights_off > cutoff:    
        warnings.append(REDUCE_SCHEDULED_ON_MSG)

    if switched_to_on_before_lights_on > cutoff or switched_to_on_after_lights_off > cutoff:    
        warnings.append(EXTEND_SCHEDULED_ON_MSG)

    return warnings

def check_switch_events_with_schedule_per_schedule_block(schedule, 
                                      override_times,
                                      override_values, 
                                      frequency_percent = .5, 
                                      after_schedule_time_min = timedelta(hours=1), 
                                      after_scheduled_time_max = timedelta(hours=4), 
                                      prior_to_scheduled_time_min = timedelta(hours=1), 
                                      prior_to_scheduled_max = timedelta(hours=2)):

    """
        Checks the "Do switch events occur freuqently and soon before/after scheduled times.
        Faults exist if the happen for more than frequency_percent of each schedule block
        
        schedule:  Schedule object
        override_times:  list of datetimes  
        override_values:  list of floats
        frequency_percent:  float in [0,1].  cutoff for what percent of any given schedule block must contain a fault for it to be reported 
        after_schedule_time_min:  timedelta.  This with after_scheduled_time_max sets a bounding box for when switch events after a scheduled change should be considered 
        after_scheduled_time_max: timedelta 
        prior_to_scheduled_time_min: timedelta. This along with prior_to_schedule_max sets a bounding box for when switch events before a scheduled change should be considered
        prior_to_scheduled_max: timedelta
    """
    from collections import defaultdict

    if not override_times:
        return []

    total_schedule_ct = defaultdict(int)

    first_time = override_times[0]
    last_time = override_times[-1]    

    schedule_block = schedule.schedule_block(first_time)
    while schedule_block.end_time < last_time:
        total_schedule_ct[(schedule_block.start_time.weekday(), schedule_block.start_time.time())] += 1
        schedule_block = schedule.schedule_block(schedule_block.end_time + timedelta(seconds=1))

    switched_to_off_before_lights_off = defaultdict(int)
    switched_to_on_before_lights_on = defaultdict(int)
    switched_to_on_after_lights_off = defaultdict(int)

    for i in range(len(override_times)):
        cur_time = override_times[i]
        cur_value = override_values[i]

        cur_schedule_block = schedule.schedule_block(cur_time)

        if cur_value == 1: #override to on
            if cur_schedule_block.value == 0:  #but the schedule says it should be off, investigate
                
                if after_schedule_time_min <= cur_time - cur_schedule_block.start_time <= after_scheduled_time_max:  #see if this is being turned on after a scheduled off time
                    switched_to_on_after_lights_off[(cur_schedule_block.start_time.weekday(), cur_schedule_block.start_time.time())] += 1                
                else: #next check to see if it is being turned on before a scheduled on time
                    next_schedule_block = schedule.schedule_block(cur_schedule_block.end_time + timedelta(seconds=1))

                    if next_schedule_block.value == 1: #next block is an on block
                        if prior_to_scheduled_time_min <= cur_schedule_block.end_time - cur_time <= prior_to_scheduled_max:
                            switched_to_on_before_lights_on[(cur_schedule_block.start_time.weekday(), cur_schedule_block.start_time.time())] += 1
            
        else: #override to off
            next_schedule_block = schedule.schedule_block(cur_schedule_block.end_time + timedelta(seconds=1))
            if next_schedule_block.value == 0:    #the next time would be off anyway so investigate
                if prior_to_scheduled_time_min <= cur_schedule_block.end_time - cur_time <= prior_to_scheduled_max:
                    switched_to_off_before_lights_off[(cur_schedule_block.start_time.weekday(), cur_schedule_block.start_time.time())] += 1



    warnings = []
    for key, value in switched_to_off_before_lights_off.iteritems():
        if value > total_schedule_ct[key] * frequency_percent:
            warnings.append((key, REDUCE_SCHEDULED_ON_MSG))

    for key, value in switched_to_on_before_lights_on.iteritems():
        if value > total_schedule_ct[key] * frequency_percent:
            warnings.append((key, EXTEND_SCHEDULED_ON_MSG))

    for key, value in switched_to_on_after_lights_off.iteritems():
        if value > total_schedule_ct[key] * frequency_percent:
            warnings.append((key, EXTEND_SCHEDULED_ON_MSG))

    return warnings

def count_number_overrides_excluding_repeated(override_times, override_values, post_override_time_to_exclude):
    """
        In order to do checks to see how the overrides are calibrated we need to filter any repeated overrides otherwise they will be double counted
        there are probably issues with this because of cases like multuple overrides in a row where eventually they will extend past the post_override_time_to_exclude bit
        assumes override_times and override_values have already been condensed to times when the value changes
    """
    override_to_on_ct = 0
    override_to_off_ct = 0

    last_override_time = None

    for i in range(len(override_times)):
        cur_time = override_times[i]
        cur_value = override_values[i]

        if last_override_time is None or (cur_time > last_override_time + post_override_time_to_exclude):
            last_override_time = cur_time
            if cur_value == 0:
                override_to_off_ct += 1
            else:
                override_to_on_ct += 1

    return override_to_on_ct, override_to_off_ct


def check_overrides_with_timeouts(override_times, 
                                  override_values, 
                                  schedule, 
                                  frequency_percent = .5, 
                                  override_timeout = timedelta(hours=2), 
                                  grace_time_before_end_of_timeout = timedelta(minutes=30), 
                                  after_override_window = timedelta(minutes=5), 
                                  only_check_when_schedule_is_off = True):
    """
        Checks the "Do switch events occur frequently and before/after timeout." cases.  Faults only exist if they happen when the lights are scheduled to be off.
        
        override_times: list of datetimes
        override_values: list of floats, len(override_times) must equal len(override_values)
        schedule:  Schedule object
        frequency_percent:  float.  This is percent of days the fault must occur on before it is reported.  
        override_timeout:  timedelta.  The length of the override timeout.
        grace_time_before_end_of_timeout: timedelta.  It is likely the operator is only concerned about large discrepancies in use.  If
                                            people are turning the lights off 5 minutes before the override expires this is not usually worth being alerted.
                                            This parameter sets the minimum time before the expiration of the timeout for the override to count as a fault.
                                            For example, if the grace period is 30 minutes and the expiration of the override is supposed to be 20:00:00 if 
                                            a user turns the lights off at 19:40:00 then this will not be counted but if they turned the lights off at 19:20:00 it would.
        after_override_window: timedelta.  Similar to the grace_time_before_end_of_timeout we are looking for cases where the override expired and an occupant was still there.
                                            The presumption is that occupants will not wait in the dark long before turning the lights on again.
                                            Any overrides to on after the window are treated as a new event and not a continuation.
                                            For example, if the window is 5 minutes, the override expired at 20:00:00,
                                            and then there is another override to on at 20:01:00 this will be counted as someone still being in the space.
                                            However if instead there was an override to on at 20:06:00 this will be treated as if one occupant left
                                            and then shortly after a new one arrived.        
        only_check_when_schedule_is_off: bool.  While this can check for any override events an operator is only likely to care about the manual
                                                overrides during off hours.  To avoid including any overrides during normal operating set this flag to True. 
    """

    res = []

    if len(override_times) < 2:  #need at least two override times to check, if there aren't then this error can't possibly happen
        return res
        
    last_time = override_times[-1]    

    number_on_overrides = 0
    number_off_overrides = 0
    
    override_to_off_early_ct = 0
    override_to_on_after_timeout_ct = 0
    
    for i in range(1, len(override_times)):
        last_time = override_times[i-1]
        cur_time = override_times[i]
        cur_value = override_values[i]
        if only_check_when_schedule_is_off:
            schedule_block = schedule.schedule_block(cur_time)
            if schedule_block.value != 0:   #skip if it is supposed to be on
                continue
                
        time_since_previous_override = cur_time - last_time

        if cur_value == 0: #override to off
            number_off_overrides += 1
            if time_since_previous_override < (override_timeout - grace_time_before_end_of_timeout):
                override_to_off_early_ct += 1
        elif cur_value == 1: #override to on
            number_on_overrides += 1
            if override_timeout < time_since_previous_override < (override_timeout + after_override_window):
                override_to_on_after_timeout_ct += 1
        else:
            raise ValueError("Invalid override value.  Override values must currently be either 0 or 1.")


    res = []

    if override_to_off_early_ct >= max(1.0, number_on_overrides * frequency_percent):
        res.append(REDUCE_OVERRIDE_TIMEOUT_MSG)

    if override_to_on_after_timeout_ct >= max(1.0, number_on_overrides * frequency_percent):
        res.append(EXTEND_OVERRIDE_TIMEOUT_MSG)

    return res


