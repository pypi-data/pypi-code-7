from setuptools import setup, find_packages
import os 
from pip.req import parse_requirements

# hack for workings with pandocs
import codecs 
try: 
  codecs.lookup('mbcs') 
except LookupError: 
  utf8 = codecs.lookup('utf-8') 
  func = lambda name, enc=utf8: {True: enc}.get(name=='mbcs') 
  codecs.register(func) 

# install readme
readme = os.path.join(os.path.dirname(__file__), 'README.md')

try:
  import pypandoc
  long_description = pypandoc.convert(readme, 'rst', format="md")
except (IOError, ImportError):
  long_description = ""

# parse requirements file
# required = [str(ir.req) for ir in parse_requirements("requirements.txt")]

# setup
setup(
  name='superss',
  version='0.2.8',
  description='RSS parsing with batteries included',
  long_description = long_description,
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ],
  keywords='',
  author='Brian Abelson',
  author_email='brian@newslynx.org',
  url='http://github.com/newslynx/superss',
  license='MIT',
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  namespace_packages=[],
  include_package_data=False,
  zip_safe=False,
  install_requires=[
    "beautifulsoup4",
    "decorator",
    "jsonpath-rw",
    "lauteur",
    "lxml",
    "ply",
    "pytz",
    "requests",
    "siegfried",
    "six",
    "tldextract",
    "wsgiref",
    "particle",
    "pageone",
    "gevent"
  ],
  tests_require=[]
)