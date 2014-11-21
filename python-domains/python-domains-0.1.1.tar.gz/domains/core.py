import re
import urlparse


_scheme_re = re.compile('^\w*:?//')


class Domain(object):
    def __init__(self, url):
        if not _scheme_re.search(url):
            url = 'http://{url}'.format(url=url)

        parts = urlparse.urlparse(url)
        netloc = parts.netloc

        # Ignore username:password
        lpart, sep, rpart = netloc.rpartition('@')
        netloc = rpart

        # *.example.com to example.com
        if netloc.startswith('*.'):
            netloc = netloc[2:]

        self.netloc = netloc

    def subdomain(self, sub):
        sub = sub.rstrip('.')

        lpart, sep, rpart = self.netloc.partition('.')
        if lpart == sub:
            return self

        return domain('{sub}.{domain}'.format(sub=sub, domain=self.netloc))

    @property
    def www(self):
        return self.subdomain('www')

    def str(self):
        return str(self)

    def __str__(self):
        return self.netloc

domain = Domain
