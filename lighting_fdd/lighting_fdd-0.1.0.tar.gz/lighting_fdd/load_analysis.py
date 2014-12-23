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


def max_load_change_at_time(load_timeseries, load_values, desired_time, band_of_time = timedelta(minutes=5)):
    """
        Calculates the max change in the range [desired_time -  band_of_time, desired_time + band_of_time]
    """
    from bisect import bisect_right

    if not load_timeseries:
        return None

    if not band_of_time:
        band_of_time = timedelta(seconds = 0)

    i = bisect_right(load_timeseries, desired_time - band_of_time)
    largest_power = -1
    smallest_power = 1e99
    ct = 0

    while i < len(load_timeseries) and (load_timeseries[i] <= (desired_time + band_of_time)):
        cur_value = load_values[i]
        largest_power = max([largest_power, cur_value])
        smallest_power = min([smallest_power, cur_value])
        ct += 1
        i += 1

    if ct < 2:
        return None

    return largest_power - smallest_power