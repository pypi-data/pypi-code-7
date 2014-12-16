"""
This module resets the :meth:qiutil.project` from ``QIN`` to ``QIN_Test``.
"""

from qiutil import project

# Reset the project name.
project(project() + '_Test')
