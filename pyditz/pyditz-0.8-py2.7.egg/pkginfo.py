"""
Package information.
"""

try:
    from . import version
    __version__ = version.__doc__.strip()
except ImportError:
    __version__ = '0.0'

__title__ = "pyditz"
__author__ = 'Glenn Hutchings'
__email__ = 'zondo42@gmail.com'
__license__ = 'LGPL v2 or later'
__copyright__ = "2013-2014, " + __author__
__url__ = "http://pypi.python.org/pypi/pyditz"

__classifiers__ = """
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)
Natural Language :: English
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Operating System :: Unix
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Topic :: Software Development :: Bug Tracking
"""
