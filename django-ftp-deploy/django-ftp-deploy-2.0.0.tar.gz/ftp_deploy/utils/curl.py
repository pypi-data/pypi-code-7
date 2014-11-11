import pycurl
import certifi

try:
    from StringIO import StringIO as _io
except ImportError:
    from io import BytesIO as _io


class curl_connection(object):

    """Helper for curl connections"""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self):
        """Authenticate curl connection"""
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.CAINFO, certifi.where())
        self.curl.setopt(self.curl.USERPWD, '%s:%s' % (self.username,
                         self.password))

    def perform(self, url):
        """Perform get request and return respond value"""
        b = _io()
        self.curl.setopt(self.curl.URL, str(url))
        self.curl.setopt(self.curl.WRITEFUNCTION, b.write)
        self.curl.perform()
        output = b.getvalue()
        return output.decode('utf-8')

    def perform_post(self, url, post):
        """Perform post request"""
        self.curl.setopt(self.curl.URL, str(url))
        self.curl.setopt(self.curl.POSTFIELDS, post)
        self.curl.perform()

    def get_http_code(self):
        """Return curl HTTP Code"""
        return self.curl.getinfo(pycurl.HTTP_CODE)

    def close(self):
        """Close curl connection"""
        self.curl.close()
