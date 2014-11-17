
class MetricType(object):
    Gauge = "gauge"
    Counter = "counter"
    Histogram = "histogram"


class MonitorType(object):
    SERVICE_CHECK = 'service check'
    METRIC_ALERT = 'metric alert'
    QUERY_ALERT = 'query alert'
    ALL = (SERVICE_CHECK, METRIC_ALERT, QUERY_ALERT)


class CheckStatus(object):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3
    ALL = (OK, WARNING, CRITICAL, UNKNOWN)
