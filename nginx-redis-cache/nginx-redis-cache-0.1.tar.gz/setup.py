try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(
  name = 'nginx-redis-cache',
  packages = ['nginx_redis_cache'], # this must be the same as the name above
  version = '0.1',
  description = 'Library to aid the integration of a Redis cache for use in Django applications sitting behind Nginx. test lib',
  author = 'Richard Hayes',
  author_email = 'rich@justcompile.it',
  url = 'https://bitbucket.org/justcompile/django-nginx-redis-cache', # use the URL to the github repo
  download_url = 'https://bitbucket.org/justcompile/django-nginx-redis-cache/get/0.1.tar.gz', # I'll explain this in a second
  keywords = ['django', 'caching', 'nginx', 'redis'], # arbitrary keywords
  classifiers = [],
  install_requires = ['django-redis']
)