#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages


setup(name='tastypie_celery_resource',
      version='0.0.3',
      description='Tastypie Resource - representation of Celery Task',
      author='Maho',
      author_email='maho@pagema.net',
      url='http://bitbucket.org/maho/tastypie_celery_resource',
      download_url= 'https://bitbucket.org/maho/tastypie_celery_resource/get/0.0.3.tar.bz2',
      scripts=[],
      license="GPL",
      keywords=["tastypie","celery"],
      packages=find_packages(),
      install_requires=['django-tastypie',"celery"],
      package_data={},
)
