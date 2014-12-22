from setuptools import setup, find_packages

setup(name='qllauncher',
      packages=find_packages(),
      version='0.6.1.2',
      author='Victor Polevoy',
      author_email='thewaveeffect@rocketmail.com',
      url='https://bitbucket.org/fx_/quakelivelauncher',
      requires=['sleekxmpp', 'requests']
      )
