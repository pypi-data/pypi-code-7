from setuptools import setup

VERSION = '0.1'

setup(name='cgi_wsgi',
      version=VERSION,
      description='A CGI-like http interface for WSGI (for educational purposes only)',
      url='http://github.com/red56/cgi_wsgi',
      download_url="https://github.com/red56/cgi_wsgi/tarball/v%s" % VERSION,
      author='Tim Diggins',
      author_email='tim@red56.co.uk',
      license='MIT',
      packages=['cgi_wsgi'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'WebTest'],
)

