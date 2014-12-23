try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
   import pypandoc
   des = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   des = open('README.md').read()

setup(
    name='quora',
    version='0.1.16',
    description=des,
    author='Christopher Su',
    author_email='chris+gh@christopher.su',
    url='https://github.com/csu/pyquora',
    packages=['quora'],
    install_requires=[
        "beautifulsoup4 == 4.3.2",
        "feedparser == 5.1.3",
        "requests==2.5.0"
    ]
)