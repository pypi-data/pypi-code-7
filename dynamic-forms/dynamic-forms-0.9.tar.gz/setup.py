from setuptools import setup, find_packages
import sys, os

version = '0.9'

setup(name='dynamic-forms',
      version=version,
      description="Django App to create dynamic Surveys",
      long_description="""\
Django App to create Surveys with multipath and multipaging support. It is designed as a Framework and therefore highly extensible.""",
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Information Technology',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
      ],
      keywords='Django Survey Framework',
      author='PythonWarriors',
      author_email='info@trea.uy',
      url='https://github.com/trea-uy/django-survey',
      license='GNU',
      packages=['dynamicForms'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'Django<1.7',
        'djangorestframework',
  	    'django-cms',
        'reportlab',
        'django-compressor',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
