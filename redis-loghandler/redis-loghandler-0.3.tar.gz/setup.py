try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='redis-loghandler',
      version='0.3',
      description='Redis logging handler',
      author='Ashwin Rajeev',
      author_email='ashwin@quadloops.com',
      url='http://www.quadloops.com',
      py_modules=['redisloghandler'],
      install_requires=['redis>=2.8.0']
      )
