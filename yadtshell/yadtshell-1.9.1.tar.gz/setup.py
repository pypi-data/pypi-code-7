#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'yadtshell',
          version = '1.9.1',
          description = '''YADT - an Augmented Deployment Tool - The Shell Part''',
          long_description = '''YADT - an Augmented Deployment Tool - The Shell Part
- regards the dependencies between services, over different hosts
- updates artefacts in a safe manner
- issues multiple commands in parallel on several hosts

for more documentation, visit http://www.yadt-project.org/
''',
          author = "Arne Hilmann, Marcel Wolf, Maximilien Riehl",
          author_email = "arne.hilmann@gmail.com, marcel.wolf@me.com, max@riehl.io",
          license = 'GNU GPL v3',
          url = 'https://github.com/yadt/yadtshell',
          scripts = ['scripts/analyze-target', 'scripts/init-yadtshell', 'scripts/sync_logs_of_all_targets', 'scripts/sync_logs_of_target.py', 'scripts/yadtshell', 'scripts/yadtshell-activate', 'scripts/yadtshellrc'],
          packages = ['yadtshell'],
          py_modules = [],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: GNU General Public License (GPL)', 'Programming Language :: Python', 'Topic :: System :: Networking', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration'],
          entry_points={
          'console_scripts':
              []
          },
          data_files = [('share/man/man1/', ['docs/man/yadtshell.1.man.gz'])],   #  data files
             # package data
          install_requires = [ "PyYAML", "Twisted", "docopt", "hostexpand", "simplejson" ],
          
          zip_safe=True
    )
