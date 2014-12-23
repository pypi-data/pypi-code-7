from setuptools import setup

VERSION = '0.0.1'

def readme():
  with open('README.md') as f:
    return f.read()

setup(
  name = 'foxtrot-client',
  packages = ['foxtrot'],
  version = VERSION,
  description = 'Foxtrot Client Library',
  long_description = readme(),
  author = 'Yasyf Mohamedali',
  author_email = 'yasyf@foxtrot.io',
  url = 'https://github.com/FoxtrotSystems/api-client-python',
  download_url = 'https://github.com/FoxtrotSystems/api-client-python/tarball/' + VERSION,
  license='MIT',
  keywords = ['foxtrot', 'route optimization'],
  install_requires = ['requests']
)
