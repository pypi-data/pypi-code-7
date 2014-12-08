#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pybuilder-django-enhanced-plugin',
          version = '0.0.7',
          description = '''Plugin for pybuilder providing some useful tasks for django development''',
          long_description = '''pybuilder-django-enhanced-plugin is a plugin for pybuilder that provides
utilities to develop, build and deploy django projects.
''',
          author = "Mirko Rossini",
          author_email = "mirko.rossini@ymail.com",
          license = 'BSD License',
          url = 'https://github.com/MirkoRossini/pybuilder_django_enhanced_plugin',
          scripts = [],
          packages = ['pybuilder_django_enhanced_plugin', 'pybuilder_django_enhanced_plugin.tasks'],
          py_modules = [],
          classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: Implementation :: CPython', 'Programming Language :: Python :: Implementation :: PyPy', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Programming Language :: Python :: 3.4', 'Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: BSD License', 'Topic :: Software Development :: Build Tools', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "django" ],
          
          zip_safe=True
    )
