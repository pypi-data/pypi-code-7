#!/usr/bin/python
#
#  (C) Catchoom Technologies S.L.
#  Licensed under the MIT license.
#  https://github.com/catchoom/craftar-python/blob/master/LICENSE
#  All warranties and liabilities are disclaimed.

"""CraftAR Python Library
==========================

The CraftAR Python Library allows you to integrate
`CraftAR Image Recognition`_ in your applications and services.

This client library provides access to our APIs:

-  `CraftAR Recognition API` allows visual recognition against one of
   your collections of reference images specified using the
   collection token.
-  `CraftAR Management API` allows upload and management of
   collections of reference images. All requests must be
   authenticated using your management api key.

The library also provides tools for performing batch operations:

-  `craftar\_search`, for image recognition.
-  `craftar\_upload`, for batch upload of images.

To use our service you need a `CraftAR`_ account.

You can get our `code`_, check the `README`_ and file bugs in the
`issue tracker`_.

.. _CraftAR: https://my.craftar.net
.. _Catchoom: http://catchoom.com
.. _code: https://github.com/Catchoom/craftar-python
.. _README: https://github.com/Catchoom/craftar-python/blob/master/README.md
.. _issue tracker: https://github.com/Catchoom/craftar-python/issues
"""
from distutils.core import setup


setup(name='craftar',
      version='1.3.2',
      description="CraftAR Python Library",
      long_description=__doc__,
      license="MIT",
      keywords="catchoom craftar image recognition",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: Information Technology",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Scientific/Engineering :: Image Recognition",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Utilities",
      ],
      platforms=["any"],
      author='Catchoom',
      author_email='support@catchoom.com',
      maintainer='Catchoom',
      maintainer_email='support@catchoom.com',
      url='http://catchoom.com',
      bugtrack_url="https://github.com/Catchoom/craftar-python/issues",
      packages=["craftar"],
      scripts=['bin/craftar_search', 'bin/craftar_upload'],
      install_requires=["requests==2.4.1", "Pillow==2.5.3"]
      )
