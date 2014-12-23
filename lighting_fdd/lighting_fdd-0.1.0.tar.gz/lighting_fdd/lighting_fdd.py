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

class Lighting_FDD(object):
    def __init__(self, 
                 implemented_schedule,                  
                 relay_timeseries, 
                 override_timeseries, 
                 intended_schedule = None,
                 load_timeseries = None, 
                 expected_load_min_change = None, 
                 expected_load_max_change = None, 
                 time_zone = None, 
                 relay_time_comparison_epsilon = timedelta(minutes=5), 
                 override_timeout = timedelta(hours=2),
                 system_time_vs_real_time_timeseries = None,
                 compress_overrides_to_change_of_state = True):
        """        
        implemented_schedule and intended_schedule: must be a list of tuples of the form (day of week and time, value) 
        intended schedule is optional
        day of week and time formatted like "%A %H:%M:%S"  
        value in {0,1} where 0 is off and 1 is on
        
        All *_schedule items (if used) must be a list of (timestamp, value) pairs or a filename of a csv containing same.  Timestamp can be any format that can be handled by
        the dateutil.parser.
        
        expected_load_min_change and expected_load_max_change:  floats.  They are to establish a band of expected load change when the lights go on/off.

        relay_time_comparison_epsilon:  timedelta.  It defines a window to allow some lag between actuation and the sensor readings.  
        It is used when checking a point in the relay_timeseries against the schedule and will allow on either side of the schedule actuation point to not be counted as errors.
        For example:  If the schedule is off at 6pm and the relay_timeseries takes until 6:02 then using the default value this would not be reported as an error.
                      However if relay_time_comparison_epsilon = timedelta(minutes=1) was used instead this would be an an error since 6:02 is more than one minute later than the schedule
        
        override_timeout: timedelta.  It is how long the override is configured to last   
        
        system_time_vs_real_time_timeseries:  List of (datetime, datetime) pairs.  If there is a known "real_time" that differs from the system time then this represents how they relate.
                                              This should be a timeseries where the value is also a timestamp.  The first timestamp represents the system time while the 
                                              second represents what the real time is at that system time.
           
        compress_overrides_to_change_of_state:  bool.  Override data can be (at least) two forms:  polled or interrupt driven.  In the polled case
                                                the state of the switch is recorded every X seconds.  As a result the actual overrides are happening
                                                when the values in the stream change state.  In the interrupt case the switch state is only recorded when it
                                                is hit.  In the polled case the stream needs to be compressed to when the value changes while in the interrupt case
                                                the stream shouldn't be altered.  This parameter governs whether this compression takes place.
        """
        from Schedule import schedule_factory
        from util import to_timeseries, to_timezone, compress_to_change_of_values

        self.time_zone = to_timezone(time_zone)
        self.implemented_schedule = schedule_factory(implemented_schedule, "Implemented schedule")
        self.intended_schedule = schedule_factory(intended_schedule, "Intended schedule")
        self.relay_timeseries = to_timeseries(relay_timeseries, self.time_zone)
        self.override_timeseries = to_timeseries(override_timeseries, self.time_zone)
        if compress_overrides_to_change_of_state:
            self.override_timeseries = compress_to_change_of_values(self.override_timeseries)
        self.load_timeseries = to_timeseries(load_timeseries, self.time_zone)
        self.expected_load_min_change = expected_load_min_change
        self.expected_load_max_change = expected_load_max_change
        self.relay_time_comparison_epsilon = relay_time_comparison_epsilon
        self.override_timeout = override_timeout
        self.system_time_vs_real_time_timeseries = system_time_vs_real_time_timeseries
        

    def get_faults(self):
        """
            Checks to see if there are any faults or suggestions for improvement.  
            Returns 4 lists: faults_with_implemented_schedule, faults_with_intended_schedule, schedule_change_suggestions, override_timeout_suggested_changes
            Any faults will be listed in the appropriate list.  If there are none for a given type the list will be empty
            
            faults_with_implemented_schedule, faults_with_intended_schedule: will have a text field that explains the fault, 
            and start_time and stop_time fields that indicate when the fault begins and ends.
            
            schedule_change_suggestions, override_timeout_change_suggestions:  These are more holistic in nature and are not constrained
            temporally like the above faults.  As such they will just contain text explaining the suggested improvement(s)
        """
        from system_fault_checks import system_fault_check
        from suggested_schedule_changes import suggested_schedule_changes
        from suggested_override_timeout_changes import suggested_override_timeout_changes
        from util import days_in_timeseries
        
        override_times = None
        override_values = None
        if len(self.override_timeseries) > 0:
            override_times, override_values = zip(*self.override_timeseries)
            
        load_times = None
        load_values = None
        if self.load_timeseries:
            load_times, load_values = zip(self.load_timeseries)

        faults_with_implemented_schedule = system_fault_check(self.implemented_schedule, 
                                               self.relay_timeseries, 
                                               override_times,
                                               override_values, 
                                               load_times,
                                               load_values, 
                                               self.expected_load_min_change, 
                                               self.expected_load_max_change, 
                                               self.relay_time_comparison_epsilon, 
                                               self.override_timeout,
                                               self.system_time_vs_real_time_timeseries)

        total_number_of_days = len(days_in_timeseries(self.relay_timeseries))
                
        faults_with_intended_schedule = None
        if self.intended_schedule:        
            faults_with_intended_schedule = system_fault_check(self.intended_schedule, 
                                               self.relay_timeseries, 
                                               override_times,
                                               override_values, 
                                               load_times,
                                               load_values, 
                                               self.expected_load_min_change, 
                                               self.expected_load_max_change, 
                                               self.relay_time_comparison_epsilon, 
                                               self.override_timeout,
                                               self.system_time_vs_real_time_timeseries)                

        schedule_change_suggestions = suggested_schedule_changes(self.implemented_schedule, override_times, override_values, total_number_of_days)
        
        override_timeout_change_suggestions = suggested_override_timeout_changes(override_times, override_values, self.override_timeout, self.implemented_schedule)

        return faults_with_implemented_schedule, faults_with_intended_schedule, schedule_change_suggestions, override_timeout_change_suggestions        

