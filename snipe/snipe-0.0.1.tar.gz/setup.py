from setuptools import setup, find_packages
import sys

install_requires = ['evernote', 'clint', 'keyring']

if sys.version_info < (2, 7):
    install_requires.append('argparse')

setup(name='snipe',
      version='0.0.1',
      description='Evernote command line tool',
      author='Yoshihiko Nishida',
      author_email='nishida@ngc224.org',
      url='https://github.com/ngc224/snipe',
      packages=find_packages(),
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      snipe = snipe.snipe:main
      """,)
