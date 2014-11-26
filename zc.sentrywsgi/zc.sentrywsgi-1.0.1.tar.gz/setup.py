##############################################################################
#
# Copyright (c) 2014 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import setuptools

VERSION = "1.0.1"


setuptools.setup(
    name="zc.sentrywsgi",
    version=VERSION,
    author="Zope Corporation",
    author_email="info@zope.com",
    description="Sentry configuration middleware.",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Framework :: Paste",
        ],
    license="ZPL 2.1",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["zc"],
    entry_points={
        "paste.filter_app_factory": [
            "sentry = zc.sentrywsgi:filter_factory",
            ],
        },
    install_requires=[
        "corbeau",
        "raven",
        "requests >=1.2.1",
        "setuptools",
        ],
    include_package_data=True,
    zip_safe=False,
    )
