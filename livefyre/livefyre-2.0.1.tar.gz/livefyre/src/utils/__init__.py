import re, pickle
import sys as _sys

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


pyver = float('%s.%s' % _sys.version_info[:2])


def _unicode(s, encoding='utf-8', errors='strict'):
    if pyver < 3.0:
        return unicode(str(s), encoding, errors)
    else:
        return s.decode(encoding)


def force_unicode(s, encoding='utf-8', errors='strict'):
    if (pyver < 3.0 and isinstance(s, unicode)) or (pyver >= 3.0 and isinstance(s, str)):
        return s
    if not isinstance(s, basestring,):
        if hasattr(s, '__unicode__'):
            s = _unicode(s)
        else:
            try:
                s = _unicode(str(s), encoding, errors)
            except UnicodeEncodeError:
                if not isinstance(s, Exception):
                    raise
                s = _unicode(' '.join([force_unicode(arg, encoding, errors) for arg in s]))
    elif not isinstance(s, unicode):
        s = s.decode(encoding, errors)
    return s
    
    
def match_url_regex(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url)


def is_valid_full_url(value):
    if match_url_regex(value):
        return True
    
    if value:
        value = force_unicode(value)
        scheme, netloc, path, query, fragment = urlparse.urlsplit(value)
        try:
            netloc = netloc.encode('idna') # IDN -> ACE
        except UnicodeError: # invalid domain part
            raise
        if pyver > 3.0:
            netloc = netloc.decode('utf-8')
        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
        return match_url_regex(url)
    else:
        raise


def get_network_from_core(core):
    if hasattr(core, 'site'):
        return core.site.network
    elif hasattr(core, 'network'):
        return core.network
    else:
        return core
