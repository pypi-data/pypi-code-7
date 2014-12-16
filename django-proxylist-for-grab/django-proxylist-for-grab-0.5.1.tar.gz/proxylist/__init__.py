from datetime import datetime

default_app_config = 'proxylist.apps.ProxylistConfig'


def now():
    now = datetime.now
    try:
        from django.utils.timezone import now
    except ImportError:
        pass
    return now()


def parse(val):
    from dateutil.parser import parse as _parse
    from django.conf import settings

    if settings.USE_TZ:
        return _parse(val)
    return _parse(val).replace(tzinfo=None)


try:
    import signals
except ImportError:
    pass
