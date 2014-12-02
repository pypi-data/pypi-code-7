#!/usr/local/bin/python

""" Configuration for the eGenix mxODBC Connect Client

    Copyright (c) 2008-2014, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
    
"""
from mxSetup import mx_Extension, mx_version
import sys

#
# Package version
#
version = mx_version(2, 1, 2)

#
# Setup information
#
name = "egenix-mxodbc-connect-client"

#
# Meta-Data
#
description = "eGenix mxODBC Connect Client for Python"
long_description = """\
eGenix mxODBC Connect Client - Python Database Interface
--------------------------------------------------------

mxODBC Connect is a client-server product from eGenix that enables
fast, easy and secure access from any Python application to remote
databases on your network, using the same well-established mxODBC
Python DB-API 2.0 compatible API.

Cross-Platform Database Access
------------------------------

Unlike our mxODBC Python ODBC Interface, mxODBC Connect is designed as
client-server application, so you no longer need to find production
quality ODBC drivers for all the client platforms you target with your
Python application.

Instead you use an easy to install royalty-free Python client library
which connects directly to the mxODBC Connect database server over the
network.

This makes mxODBC Connect the ideal basis for writing cross-platform
multi-tier database applications in Python, especially if you develop
applications that need to communicate with databases such as MS SQL
Server and MS Access, Oracle Database, IBM DB2 and Informix, Sybase
ASE and Sybase Anywhere, MySQL, PostgreSQL, SAP MaxDB and many more,
that run on remote Windows or Linux machines.

Centralized Database Access Administration
------------------------------------------

By removing the need to install and configure ODBC drivers on the
client side, mxODBC Connect greatly simplifies setup, rollout and
configuration of database driven client applications, while at the
same time making the network communication between client and database
server more efficient and more secure.

Server Packages
---------------

The mxODBC Connect Server packages includes the server application of
the eGenix.com mxODBC Connect Database Interface for Python and are
available for Linux and Windows as 32- and 64-bit application.

They are distributed as installers which have to be downloaded from
our product web page (see below).

Client Package
--------------

mxODBC Connect Client package is distributed as pure Python package
and works on most platforms where you can run Python.

It's an add-on to our open-source eGenix.com mx Base Distribution
("egenix-mx-base" on PyPI):

    http://www.egenix.com/products/python/mxBase/
    https://pypi.python.org/pypi/egenix-mx-base/

The client package is available from our product page (see below) and
as "egenix-mxodbc-connect-client" package on PyPI:

    https://pypi.python.org/pypi/egenix-mxodbc-connect-client/

Downloads
---------

For downloads, documentation, changelog, evaluation and production
licenses, please visit the product page at:

    http://www.egenix.com/products/python/mxODBCConnect/

Web Installer
-------------

The source package on the Python Package Index (PyPI) is a web
installer, which will automatically select and download the right
binary for your installation platform.

Licenses
--------

For evaluation and production server licenses, please visit our
product page at:

    http://www.egenix.com/products/python/mxODBCConnect/#Licensing

The clients can be used free of charge and don't require installation
of licenses.

This software is brought to you by eGenix.com and distributed under
the eGenix.com Commercial License 1.3.0.
"""
license = (
"eGenix.com Commercial License 1.3.0; "
"Copyright (c) 2008-2014, eGenix.com Software GmbH, All Rights Reserved"
)
author = "eGenix.com Software GmbH"
author_email = "info@egenix.com"
maintainer = "eGenix.com Software GmbH"
maintainer_email = "info@egenix.com"
url = "http://www.egenix.com/products/python/mxODBCConnect/"
download_url = 'https://downloads.egenix.com/python/download_url/%s/%s/' % (
    name,
    version)
platforms = [
    'Windows',
    'Linux',
    'FreeBSD',
    'Solaris',
    'Mac OS X',
    ]
classifiers = [
    "Environment :: Console",
    "Environment :: No Input/Output (Daemon)",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
    "Operating System :: Other OS",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    "Topic :: Database",
    "Topic :: Database :: Database Engines/Servers",
    "Topic :: Database :: Front-Ends",
    "Topic :: Documentation",
    "Topic :: Internet",
    "Topic :: Office/Business",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities ",
    ]
if 'alpha' in version:
    classifiers.append("Development Status :: 3 - Alpha")
elif 'beta' in version:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")
    classifiers.append("Development Status :: 6 - Mature")
classifiers.sort()

#
# Dependencies
#
if sys.version[:3] >= '2.5':
    # mxODBC Connect extends egenix-mx-base; Note: the package name has to
    # be given using underscores, since setuptools doesn't like hyphens in
    # package names.
    requires = ['egenix_mx_base']

#
# Pure Python modules
#
packages = ['mx.ODBCConnect',
            'mx.ODBCConnect.Common',
            'mx.ODBCConnect.Client',
            'mx.ODBCConnect.Misc',
            ]

#
# Data files
#
data_files = [

    # Product documentation
    'mx/ODBCConnect/Doc/mxODBCConnect.pdf',
    'mx/ODBCConnect/Doc/mxODBC.pdf',
    'mx/ODBCConnect/Doc/eGenix.com-Third-Party-Licenses-2.0.pdf',
    'mx/ODBCConnect/Doc/client-config.ini',

    # Standard product files
    'mx/ODBCConnect/COPYRIGHT',
    'mx/ODBCConnect/LICENSE',
    'mx/ODBCConnect/README',

]

# Declare namespace packages (for building eggs)
namespace_packages = [
    'mx',
    ]
