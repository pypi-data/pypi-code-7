from setuptools import setup, find_packages
import sys
import snipe.config as config

install_requires = ['evernote', 'clint', 'keyring']

if sys.version_info < (2, 7):
    install_requires.append('argparse')

long_description = """\
snipe is snippet command-line tool in cooperation with evernote.

Setup user config ::

    $ snipe --config
    Get Evernote DeveloperToken URL --> https://www.evernote.com/api/DeveloperToken.action
    DeveloperToken: <developer token>
    Set search tag / Default is 'snipe'
    Search tag: <tag>
    Set search max limit / Default is 50
    Search limit: <limit>

View the note list ::

    $ snipe
    search --> tag:'<tag>' limit:<limit>
    No 1 : <title>
    No 2 : <title>
    No 3 : <title>
    ...

Enter a Number to output a note content ::

    $ snipe 2
    <content>
    ...
"""

setup(name=config.application_name,
      version=config.version,
      description='Evernote command line tool',
      long_description=long_description,
      author='Yoshihiko Nishida',
      author_email='nishida@ngc224.org',
      url='https://github.com/ngc224/snipe',
      packages=find_packages(),
      install_requires=install_requires,
      license='GPLv3',
      keywords='Evernote',
      entry_points="""
      [console_scripts]
      snipe = snipe.snipe:main
      """,)
