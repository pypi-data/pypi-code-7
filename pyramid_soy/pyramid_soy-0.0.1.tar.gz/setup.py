import os

from setuptools import find_packages
from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()

requires = [
    'soy'
]

setup(name='pyramid_soy',
      version='0.0.1',
      description='Simple soy wrapper with simple cache.',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='winkidney',
      author_email='winkidney@gmail.com',
      url='http://github.com/winkidney',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      scripts=['setup.py',],
      install_requires=requires,
      tests_require=requires,
      )
