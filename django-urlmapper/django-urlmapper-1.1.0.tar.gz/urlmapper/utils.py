import re
import functools

from django.contrib.admindocs.views import simplify_regex
from django.core.urlresolvers import RegexURLPattern, RegexURLResolver


def get_urls(patterns, sort=False):
    urls = []
    found = get_patterns(patterns)

    for base, pattern in found:
        func = pattern.callback
        if isinstance(func, functools.partial):
            func = func.func

        func_name = get_name(func)
        regex = base + pattern.regex.pattern

        urls.append(dict(
            view="{0}.{1}".format(func.__module__, func_name),
            name=pattern.name or "",
            path=simplify_regex(regex),
            args=pattern.default_args,
        ))

    if sort:
        urls = sorted(urls, key=lambda x: x["path"])

    return urls


def get_name(func):
    if hasattr(func, "__name__"):
        return func.__name__
    elif hasattr(func, "__class__"):
        return "%s()" % func.__class__.__name__
    else:
        return re.sub(r" at 0x[0-9a-f]+", "", repr(func))


def get_patterns(patterns, base=""):
    for p in patterns:
        if isinstance(p, RegexURLPattern):
            yield (base, p)
        elif isinstance(p, RegexURLResolver):
            for p in get_patterns(p.url_patterns, base + p.regex.pattern):
                yield p
        else:
            raise TypeError(
                "%s does not appear to be a url pattern" % p,
            )
