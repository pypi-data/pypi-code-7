# -*- coding: utf-8 -*-
'''
Created on Feb 23, 2014

Speed based segmnetation module

@author: curiel
'''

from collections import OrderedDict


class Interval(object):
    '''Represents a time interval'''
    
    def __init__(self):
        self.lower_limit = None
        self.upper_limit = None
        self.data = OrderedDict()

    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        '''Add an item just if key is part of the integer sequence
           induced by key1,...,keyn in self.keys()
        '''
        if isinstance(key, int):
            if self.upper_limit != None:
                if self.upper_limit + 1 == key:
                    self.data[key] = value
                    self.upper_limit = key
                elif self.lower_limit <= key <= self.upper_limit:
                    self.data[key] = value
                else:
                    raise KeyError("Key must be the next in the sequence")
            else:
                self.lower_limit = key
                self.upper_limit = key
                self.data[key] = value
        else:
            raise KeyError("Key must be an integer value")
        
    def __delitem__(self, key):
        '''Deletes an item at the beginning or ending of the sequence'''
        if key in [self.lower_limit, self.upper_limit]:
            del self.data[key]
            if len(self.data) == 0:
                self.lower_limit = None
                self.upper_limit = None
            elif key == self.lower_limit:
                self.lower_limit = key + 1
            else:
                self.upper_limit = key - 1
            return
        raise KeyError("Key must be the first or last element of the interval")
        
    def __len__(self):
        return len(self.data)
    
    def pop(self):
        '''Pop an interval item from the tail'''
        if len(self.data) > 0:
            old_upper_limit = self.upper_limit
            self.upper_limit -= 1
            if self.upper_limit < self.lower_limit:
                self.upper_limit = None
                self.lower_limit = None
            return (old_upper_limit, 
                    self.data.pop(old_upper_limit))
        else:
            raise KeyError("Interval empty")
        
    def popleft(self):
        '''Pop an interval item from the head'''
        if len(self.data) > 0:
            old_lower_limit = self.lower_limit
            self.lower_limit += 1
            if self.upper_limit < self.lower_limit:
                self.upper_limit = None
                self.lower_limit = None
            return (old_lower_limit,
                    self.data.pop(old_lower_limit))
        else:
            raise KeyError("Interval empty")
        
    def limits(self):
        '''Get the limits of this interval'''
        if len(self.data) == 0:
            return "Empty"
        return (self.lower_limit, self.upper_limit)
    
    def keys(self):
        return self.data.keys()
    
    def __str__(self):
        return str(self.limits()) + ":" + str(self.data)
    
    __repr__ = __str__
    

class TCIInterval(Interval):
    '''Interval to be used with the IRIT-TCI tracker'''
    
    def __init__(self, driver, is_movement_interval):
        super(TCIInterval, self).__init__()
        self.driver = driver
        self.is_movement_interval = is_movement_interval
    
    @property
    def is_static_interval(self):
        '''Checks if it is an static interval'''
        return not self.is_movement_interval
    
    @is_static_interval.setter
    def is_static_interval_setter(self, value):
        self.is_movement_interval = not value
    
        
class IntervalList(object):
    
    def __init__(self, speed_threshold,
                 articulators=['right_hand', 'left_hand'],
                 driver="right_hand", 
                 starting_interval_mv=False):
        '''Initialization of interval list for two hands'''

        self.sequences = {}
        self.current_intervals = {}
        for articulator in articulators:
            self.sequences[articulator] = []
            self.current_intervals[articulator] = TCIInterval(
                                                        articulator,
                                                        starting_interval_mv
                                                        )
        self.speed_threshold = speed_threshold
    
#     def include(self, new_frame_data):
#         '''new_frame_data is a row in a pandas dataframe'''
#         for articulator in self.sequences.keys():
#             results = self.include_in_articulator_interval_2window(
#                                                                 articulator,
#                                                                 new_frame_data)
#             if results:
#                 for result in results:
#                     self.notification_context.send_to_channels(
#                                                         {articulator:result}
#                                                         )

    def include_in_articulator_interval_2window(self, 
                                        driver,
                                        new_frame_data):
        '''Creates an individual segmentation for each articulator'''

        # Get the pertinent information for the
        # specified articulator (driver)
        new_frame = int(new_frame_data['frame'])
        driver_speed = float(new_frame_data[driver+'_v'])
        current_interval = self.current_intervals[driver]
        
        # Sequence has the particular sequence of intervals for 'driver'
        sequence = self.sequences[driver]
        
        # Check how to add data to our interval list
        if len(current_interval) == 0:
            # Mostly, the first case
            current_interval[new_frame] = new_frame_data
            current_interval.driver = driver
            if driver_speed < self.speed_threshold:
                current_interval.is_movement_interval = False
            else:
                current_interval.is_movement_interval = True
        else:
            # Check if movement or static posture
            if driver_speed < self.speed_threshold:
                # This is an static posture, hands aren't moving
                # We check if the current interval is a movement interval
                if current_interval.is_movement_interval:
                    # We are in a movement interval, so new_frame data
                    # must be the second frame of a new static interval
                    # and the last frame of the current_interval is
                    # transferred to the new interval
                    new_first_frame = None
                    if len(current_interval) > 1:
                        new_first_frame = current_interval.upper_limit
                        last_frame_data = current_interval[
                                                    current_interval.upper_limit]
                        del current_interval[current_interval.upper_limit]
                    
                    # We detect movement minimums on the closing interval
                    # to create new sub static intervals, if necessary
                    #results = self.cut_minimums(current_interval)
                    results = self.cut_minimums_2window(current_interval)
                    
                    # Adds the found segmentation to the running sequence
                    sequence += results
                    
                    # we create a new empty static interval before closing
                    current_interval = TCIInterval(driver, 
                                                   is_movement_interval=False)
                    # Add data to the new interval
                    if new_first_frame:
                        current_interval[new_first_frame] = last_frame_data
                    current_interval[new_frame] = new_frame_data
                    self.current_intervals[driver] = current_interval
                    
                    # we return the found segmentation (or the movement
                    # interval if it's the case)
                    return results
                        
                # we explicitly return None to omit the 'else' cases,
                # indicating by the way that there was no new interval
                # created (static posture in static interval)
                
                # Add to current static interval
                current_interval[new_frame] = new_frame_data
                
                return None

            # If we are here, this is a movement
            # We check if the current interval is static
            if current_interval.is_static_interval:
                # We are in an static interval, we need to change it because
                # we are dealing with a movement posture

                # Here we only have one possibility, add the last interval
                # to the proper sequence 
                sequence.append(current_interval)
                
                # We save the interval data just to return it
                results = current_interval
                
                # we create a new empty static interval before closing
                current_interval = TCIInterval(driver, 
                                               is_movement_interval=True)
                
                # Add movement data to the new interval
                current_interval[new_frame] = new_frame_data
                
                # Register the new movement interval as the current interval
                self.current_intervals[driver] = current_interval
                
                # Returns the static interval
                return [results]

            # Add info to current movement interval (movement posture 
            # movement interval)    
            current_interval[new_frame] = new_frame_data
            
            # We explicitly return for esthetic purposes
            return None

    def include_in_articulator_interval(self, 
                                        driver,
                                        new_frame_data):
        '''Creates an individual segmentation for each articulator'''

        # Get the pertinent information for the
        # specified articulator (driver)
        new_frame = int(new_frame_data['frame'])
        driver_speed = float(new_frame_data[driver])
        current_interval = self.current_intervals[driver]
        
        # Sequence has the particular sequence of intervals for 'driver'
        sequence = self.sequences[driver]
        
        # Check how to add data to our interval list
        if len(current_interval) == 0:
            # Mostly, the first case
            current_interval[new_frame] = new_frame_data
            current_interval.driver = driver
            if driver_speed < self.speed_threshold:
                current_interval.is_movement_interval = False
            else:
                current_interval.is_movement_interval = True
        else:
            # Check if movement or static posture
            if driver_speed < self.speed_threshold:
                # This is an static posture, hands aren't moving
                # We check if the current interval is a movement interval
                if current_interval.is_movement_interval:
                    # We are in a movement interval, so new_frame data
                    # must be the first frame of a new static interval.
                    
                    # We detect movement minimums on the closing interval
                    # to create new sub static intervals, if necessary
                    #results = self.cut_minimums(current_interval)
                    results = self.cut_minimums_2window(current_interval)
                    
                    # Adds the found segmentation to the running sequence
                    sequence += results
                    
                    # we create a new empty static interval before closing
                    current_interval = TCIInterval(driver, 
                                                   is_movement_interval=False)
                    # Add data to the new interval
                    current_interval[new_frame] = new_frame_data
                    self.current_intervals[driver] = current_interval
                    
                    # we return the found segmentation (or the movement
                    # interval if it's the case)
                    return results
                        
                # we explicitly return None to omit the 'else' cases,
                # indicating by the way that there was no new interval
                # created (static posture in static interval)
                
                # Add to current static interval
                current_interval[new_frame] = new_frame_data
                
                return None

            # If we are here, this is a movement
            # We check if the current interval is static
            if current_interval.is_static_interval:
                # We are in an static interval, we need to change it because
                # we are dealing with a movement posture

                # Here we only have one possibility, add the last interval
                # to the proper sequence 
                sequence.append(current_interval)
                
                # We save the interval data just to return it
                results = current_interval
                
                # we create a new empty static interval before closing
                current_interval = TCIInterval(driver, 
                                               is_movement_interval=True)
                
                # Add movement data to the new interval
                current_interval[new_frame] = new_frame_data
                
                # Register the new movement interval as the current interval
                self.current_intervals[driver] = current_interval
                
                # Returns the static interval
                return [results]

            # Add info to current movement interval (movement posture 
            # movement interval)    
            current_interval[new_frame] = new_frame_data
            
            # We explicitly return for esthetic purposes
            return None

    def cut_minimums(self, movement_interval):
        '''Detects speed minimums and creates static postures from them'''
        
        found_intervals = []
        last_mean_value = -1
        last_minimum_index = -1
        lower_limit = -1 
        found_peaks = 0
        articulator=movement_interval.driver
        
        if len(movement_interval) < 2:
            return [movement_interval]
        
        search_new_maximum = True

        for i in range(movement_interval.lower_limit,
                       movement_interval.upper_limit + 1):
            
            # Gets mean speed for articulator
            mean_value = movement_interval[i][articulator]
            
            if search_new_maximum:
                if last_mean_value < 0:
                    # First speed value, automatic minimum
                    lower_limit = i
                    last_minimum_index = i
                elif last_mean_value > mean_value:
                    # Speed decreased, we found a peak, 
                    # a maximum
                    found_peaks += 1
                    
                    if found_peaks >= 2:
                        # we take the last minimum
                        # as a key posture
                        new_key_posture_interval = TCIInterval(articulator, 
                                                                   is_movement_interval=False)
                        new_key_posture_interval[
                                    last_minimum_index] = movement_interval[
                                                            last_minimum_index]
                        # We create a movement interval
                        # until that point
                        new_movement_interval = TCIInterval(articulator,
                                                                is_movement_interval=True)
                        for j in range(lower_limit, last_minimum_index):
                            new_movement_interval[j] = movement_interval[j]
                        
                        found_intervals.append(new_movement_interval)
                        found_intervals.append(new_key_posture_interval)
                        
                        # We change limits
                        lower_limit = last_minimum_index + 1

                    search_new_maximum = False
                    last_mean_value = mean_value
            else:        
                # Enters here if searching minimums
                if last_mean_value < mean_value:
                    # Speed increased, we found a
                    # new minimum
                    search_new_maximum = True
                    last_minimum_index = i-1
            
            # We replace values
            last_mean_value = mean_value
        
        if search_new_maximum:
            # We were searching a maximum, take the last frame as a maximum
            found_peaks += 1
            if found_peaks >= 2:
                # we take the last minimum
                # as a key posture
                new_key_posture_interval = TCIInterval(articulator, 
                                                           is_movement_interval=False)
                new_key_posture_interval[
                            last_minimum_index] = movement_interval[
                                                    last_minimum_index]
                # We create a movement interval
                # until that point
                new_movement_interval = TCIInterval(articulator,
                                                        is_movement_interval=True)
                for j in range(lower_limit, last_minimum_index):
                    new_movement_interval[j] = movement_interval[j]
                
                found_intervals.append(new_movement_interval)
                found_intervals.append(new_key_posture_interval)
                
                # We change limits
                lower_limit = last_minimum_index + 1
                
        # We are searching a new minimum, we then just
        # take upper limit of our movement_interval
        last_movement_interval = TCIInterval(articulator,
                                                 is_movement_interval=True)
        for j in range(lower_limit, 
                       movement_interval.upper_limit + 1):
            last_movement_interval[j] = movement_interval[j]
        found_intervals.append(last_movement_interval)

        return found_intervals

    def cut_minimums_2window(self, movement_interval):
        '''Detects speed minimums and creates static postures from them'''
        
        found_intervals = []
        last_mean_value = -1
        last_minimum_index = -1
        lower_limit = -1 
        found_peaks = 0
        articulator=movement_interval.driver
        
        if len(movement_interval) <= 3:
            return [movement_interval]
        
        search_new_maximum = True

        for i in range(movement_interval.lower_limit,
                       movement_interval.upper_limit + 1):
            
            # Gets mean speed for articulator
            mean_value = float(movement_interval[i][articulator+"_v"])
            
            if search_new_maximum:
                if last_mean_value < 0:
                    # First speed value, automatic minimum
                    lower_limit = i
                    last_minimum_index = i
                elif last_mean_value > mean_value:
                    # Speed decreased, we found a peak, 
                    # a maximum
                    found_peaks += 1
                    
                    if found_peaks >= 2 and last_minimum_index - 1 > \
                        movement_interval.lower_limit:
                        
                        # We create a movement interval
                        # until that point
                        new_movement_interval = TCIInterval(articulator,
                                                                is_movement_interval=True)
                        for j in range(lower_limit, last_minimum_index):
                            new_movement_interval[j] = movement_interval[j]

                        # we take the last minimum
                        # as a key posture
                        new_key_posture_interval = TCIInterval(articulator,
                                                    is_movement_interval=False
                                                    )

                        if len(new_movement_interval) > 1:
                            # If last movement has more than one frame, we can
                            # transfer the last one to the current
                            # posture interval. This would give us the 2-window
                            # needed to take in account possible co-articulations
                            new_key_posture_interval[
                                    last_minimum_index - 1] = movement_interval[
                                                        last_minimum_index - 1]
                            del new_movement_interval[last_minimum_index - 1]
                                    
                        new_key_posture_interval[
                                last_minimum_index] = movement_interval[
                                                        last_minimum_index]

                        found_intervals.append(new_movement_interval)
                        found_intervals.append(new_key_posture_interval)
                        
                        # We change limits
                        lower_limit = last_minimum_index + 1

                    search_new_maximum = False
                    last_mean_value = mean_value
            else:        
                # Enters here if searching minimums
                if last_mean_value < mean_value:
                    # Speed increased, we found a
                    # new minimum
                    search_new_maximum = True
                    last_minimum_index = i-1
            
            # We replace values
            last_mean_value = mean_value
        
        if search_new_maximum:
            # We were searching a maximum, take the last frame as a maximum
            found_peaks += 1
            if found_peaks >= 2:
                # we take the last minimum
                # as a key posture
                new_key_posture_interval = TCIInterval(articulator, 
                                                           is_movement_interval=False)
                new_key_posture_interval[
                            last_minimum_index] = movement_interval[
                                                    last_minimum_index]
                # We create a movement interval
                # until that point
                new_movement_interval = TCIInterval(articulator,
                                                        is_movement_interval=True)
                for j in range(lower_limit, last_minimum_index):
                    new_movement_interval[j] = movement_interval[j]
                
                found_intervals.append(new_movement_interval)
                found_intervals.append(new_key_posture_interval)
                
                # We change limits
                lower_limit = last_minimum_index + 1
                
        # We are searching a new minimum, we then just
        # take upper limit of our movement_interval
        last_movement_interval = TCIInterval(articulator,
                                                 is_movement_interval=True)
        for j in range(lower_limit, 
                       movement_interval.upper_limit + 1):
            last_movement_interval[j] = movement_interval[j]
        found_intervals.append(last_movement_interval)
        
        return found_intervals

    def clean(self):
        '''Just finishes adding last interval to the sequence if
           it is not empty
        '''
        if len(self.current_intervals) > 0:
            self.sequences.append(self.current_intervals)