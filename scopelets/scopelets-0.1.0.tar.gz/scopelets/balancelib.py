# Copyright (c) 2014 Scopely, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from operator import add


def balance(instances_by_az, number):
    """
    Tries to balance given AZs
    using given number of instances.
    Once they are balanced,
    returns the fill layout
    and the remained number of instances
    """
    az_count = len(instances_by_az)
    result = [0] * az_count
    # sort AZs by number of instances,
    # but store their index as a second element
    # of the tuple
    from_min_to_max = sorted(
        zip(instances_by_az, range(0, az_count)), key=lambda x: x[0]
    )
    reminder = number
    for x in range(0, az_count - 1):
        # move through the sorted list
        # and try to fill out the gaps
        depth = from_min_to_max[x + 1][0] - from_min_to_max[x][0]
        number_needed = (x + 1) * depth
        if reminder > number_needed:
            # if there enough instances left
            # fill the current level with the needed depth
            reminder -= number_needed
            for y in range(0, x + 1):
                result[from_min_to_max[y][1]] += depth
        else:
            # if there are not enough instances
            # just try to fill the given level as evenly as possible
            actual_depth = reminder / (x + 1)
            actual_reminder = reminder % (x + 1)
            for y in range(0, x + 1):
                result[from_min_to_max[y][1]] += (
                    y < actual_reminder and actual_depth + 1 or actual_depth
                )
            reminder = 0
    return result, reminder


def fill_the_reminder(az_count, number):
    """
    Fills up AZs with the given number of instances,
    for the case when AZs are already balanced
    """
    depth = number / az_count
    reminder = number % az_count
    # just fill in the instances
    return [
        az < reminder and depth + 1 or depth for az in range(0, az_count)
    ]


def fill(instances_by_az, number):
    """
    Takes a list with the number of instances in each AZ,
    and the number or instances that you need to add.
    Returns a list with number of instances to be added to each AZ.
    """
    az_count = len(instances_by_az)
    if [instances_by_az[0]] * az_count == instances_by_az:
        # if AZs are already balanced
        # just fill them with the given number of instances
        return fill_the_reminder(az_count, number)
    else:
        # try to balance AZs first
        result, reminder = balance(instances_by_az, number)
        if reminder:
            # if they are balanced and there are some instances left
            # just try to spread them equally between AZs
            reminder_result = fill_the_reminder(az_count, reminder)
            return map(add, result, reminder_result)
        return result
