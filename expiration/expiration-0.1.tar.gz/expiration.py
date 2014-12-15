#######################################################################
# expiration manages complicated expiration rules, and will calculate
#  when abstract 'objects' have expired. It doesn't actually do
#  anything except calculate which objects have exipired. Acting on
#  this information is left to the caller.
#
# Copyright 2014 True Blade Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
########################################################################

__all__ = ['RetentionCriterion', 'RetentionRules', 'find_expired_items', 'date']

from collections import namedtuple as _namedtuple
from functools import cmp_to_key as _cmp_to_key
import datetime as _datetime
import logging as _logging

RetentionCriterion = _namedtuple('RetentionCriterion', 'selector retention_period')
RetentionRules = _namedtuple('RetentionRules', 'default_retention_period criteria')

# These are just handy examples. You can use any function you want
#  the return values should be anything that's comparable with other
#  values returned by the same function. The values don't have to be
#  comparable to values returned by other such functions.
# They're in a "namespace" just for convenience

class date:
    @staticmethod
    def year_of(timestamp):
        return timestamp.year

    @staticmethod
    def quarter_of(timestamp):
        return timestamp.year, (timestamp.month-1) // 4 + 1

    @staticmethod
    def month_of(timestamp):
        return timestamp.year, timestamp.month

    @staticmethod
    def week_of(timestamp):
        iso = timestamp.isocalendar()
        return iso[0], iso[1]

    @staticmethod
    def day_of(timestamp):
        return timestamp.toordinal()


# this will be turned in to a key function, but it's easier to write
#  the cmp function.
def _criteria_cmp(a, b):
    # None sorts first
    if a.retention_period is None and b.retention_period is None:
        return 0
    if a.retention_period is None:
        return 1
    if b.retention_period is None:
        return -1
    return a.retention_period.total_seconds() - b.retention_period.total_seconds()


def find_expired_items(items, time_key, retention_rules, asof_timestamp=None):
    if asof_timestamp is None:
        asof_timestamp = _datetime.datetime.now()

    # make sure the retention criteria are sorted, longest to shortest
    retention_criteria = sorted(retention_rules.criteria, key=_cmp_to_key(_criteria_cmp), reverse=True)

    # these map to the retention criteria rules
    first_for_rule = [None] * len(retention_criteria)

    # the items also need to be in sorted order
    for item in sorted(items, key=time_key):
        first_match = None

        for idx, criteria in enumerate(retention_criteria):
            # even after we match, keep searching. but remember the first matching criteria we found, because that's the
            #  one we want to compare our age against, since it has the longest retention criteria of our matches.
            # we keep searching because we need to fill in all of the first_for_rule values
            if first_for_rule[idx] is None or criteria.selector(time_key(first_for_rule[idx])) != criteria.selector(time_key(item)):
                _logging.debug('item %s matches criteria %s', item, criteria)
                first_for_rule[idx] = item
                if first_match is None:
                    first_match = criteria

        # if we didn't match any criteria, compare against the default retention_period
        if first_match:
            retention_period = first_match.retention_period
        else:
            _logging.debug('item %s no match, using default retention', item)
            retention_period = retention_rules.default_retention_period

        # if the retention period is None, we never delete
        item_age = asof_timestamp - time_key(item)
        delete = retention_period is not None and item_age > retention_period

        if delete:
            yield item, first_match

