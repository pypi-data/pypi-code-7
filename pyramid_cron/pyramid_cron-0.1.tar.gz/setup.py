from __future__ import print_function

import os
from setuptools import setup, find_packages


setup(name='pyramid_cron',
      version='0.1',
      description='Simple scheduled tasks for Pyramid.',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Framework :: Pyramid',
      ],
      keywords='pyramid scheduled tasks cron',
      url='http://github.com/cartlogic/pyramid_cron',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=[
          'Pyramid>=1.4.5',
          'six',
      ],
      license='MIT',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
