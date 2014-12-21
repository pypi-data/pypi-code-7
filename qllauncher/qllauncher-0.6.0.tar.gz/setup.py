from setuptools import setup, find_packages

setup(name='qllauncher',
      packages=find_packages(),
      version='0.6.0',
      author='Victor Polevoy',
      author_email='contact@vpolevoy.com',
      url='https://bitbucket.org/fx_/quakelivelauncher',
      requires=['sleekxmpp', 'requests']
      )