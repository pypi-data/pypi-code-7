from __future__ import unicode_literals
import os
from setuptools import setup, find_packages

import musette

def read(filepath):
    return open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
    ).read()

README = read('README.rst')

version = ".".join(map(str, musette.__version__))
author = musette.__author__
description = musette.__doc__

setup(name='musette',
      version=version,
      description=description,
      long_description=README,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Information Technology',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          'License :: OSI Approved :: MIT License',
          'Framework :: Django'
      ],
      keywords='django environment variables 12factor os.environ',
      author=author,
      author_email='gmflanagan@outlook.com',
      url='http://github.com/averagehuman/musette',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      test_suite='musette.test.load_suite',
      zip_safe=False,
)

