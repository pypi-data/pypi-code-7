from json import JSONEncoder
import datetime
from isodate import parse_duration, duration_isoformat, datetime_isoformat

ramp_result_stream_name = lambda ramp_class_name: "_ramp_result_%s" % ramp_class_name


def percentile_from_dict(D, P):
    """
    Find the percentile of a list of values

    @parameter N - A dictionary, {observation: frequency}
    @parameter P - An integer between 0 and 100

    @return - The percentile of the values.
    """
    assert 0 < P <= 100, "Percentile must be in range (0, 100)"
    N = sum(D.values())
    P = float(P)/100
    n = int(N) * P

    i = 1  # The formula returns a 1-indexed number
    observation = None
    for observation in sorted(D.keys()):
        if i >= n:
            return observation
        i += D[observation]
    return observation
    # raise AssertionError("Didn't find percentile")


class DateTimeAwareJsonEncoder(JSONEncoder):
    def default(self, o):
        if type(o) == datetime.timedelta:
            return duration_isoformat(o)
        elif type(o) == datetime.datetime:
            return datetime_isoformat(o)
        return super(DateTimeAwareJsonEncoder, self).default(o)


def set_timeouts_on_socket(scket):
    scket.RCVTIMEO = 10000
    scket.SNDTIMEO = 10000
    scket.LINGER = 1000