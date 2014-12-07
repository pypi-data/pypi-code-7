
"""
Time utilities
A collection of time utilities used mostly to process various formats of
cache item expiration. May be used across all cache adapters that support
cache items expiration.
"""
from datetime import datetime
import arrow
from . import exceptions


def ttl_from_expiration(expires):
    """
    TTL from expiration
    Returns ttl in seconds until expiration date based on now.

    :param expires:             date/timestamp/string/shift (+ 1 hour)
    :return:                    int
    """

    now = int(datetime.utcnow().timestamp())
    expires = expires_to_timestamp(expires)
    return expires - now



def expires_to_timestamp(expires):
    """
    Expires to timestamp
    Converts expiration to a unix timestamp.  The expiration date may be in
    one of the formats:

        - datetime, naive or timezone-aware
        - arrow object
        - timestamp string or int
        - date string
        - time shift (+1day 1hour, +1week -1day)

    All ow the above are implied to be in UTC format for the exception on
    datetime and arrow objects having explicit timezone set (those will be
    converted to UTC). Yet naive datetimes will are implied to be UTC as well.

    :param expires:             mixed, expiration date
    :return:                    int, timestamp
    """

    # from timestamp (no conversion)
    if isinstance(expires, int):
        return expires
    if isinstance(expires, str) and expires.isdigit():
        return int(expires)


    # from datetime or arrow
    if isinstance(expires, datetime) or isinstance(expires, arrow.Arrow):
        arr = expires
        if isinstance(expires, datetime):
            arr = arrow.get(expires)

        arr = arr.to('UTC')
        arr.replace()
        return arr.timestamp

    # from time shift
    if expires.startswith('+') or expires.startswith('-'):
        params = time_shift_to_params(expires)
        arr = arrow.utcnow().replace(**params)
        return arr.timestamp


    # from date string
    arr = arrow.get(expires)
    return arr.timestamp


def time_shift_to_params(shift):
    """
    Time shift to params
    Converts arbitrary time shift string to a dictionary of parameters. It
    can parse pretty complex shifts like for example this one although it does
    not make much sense in real applications:

    '+2day-12years10 Seconds + 2 months3zz '

    All parameters will be lower cased and there is no point in passing one
    type of parameters more than once, invalid parameters will raise
    ValueException si you know if you misspelled. If parameter does not
    include an operation sign the previous found sign will be used,
    for example: '+1years2months' will be considered as +1 year and +2 months.

    :param shift:               string, time shift
    :return:                    dict, parameters
    """

    import re
    valid = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds']

    pattern = r'([+|-]*)\s*(\d*)\s*([a-z]+)'
    result = re.findall(pattern, shift.lower())

    params = dict()
    previous_sign = None
    for sign, how_much, of_what in result:
        if not sign:
            sign = previous_sign

        of_what = of_what.rstrip('s') + 's'
        if not of_what in valid or not how_much:
            error = '[{}] is not a valid time shift!'.format(shift)
            raise exceptions.ValueException(error)

        params[of_what] = int(sign+how_much)
        previous_sign = sign


    if not params:
        error = '[{}] is not a valid time shift!'.format(shift)
        raise exceptions.ValueException(error)

    return params





