# -*- coding: utf-8 -*-

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from sphinxcontrib.emacs import __version__

needs_sphinx = '1.2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinxcontrib.emacs',
]

default_role = 'code'

source_suffix = '.rst'

master_doc = 'index'

project = u'sphinxcontrib-emacs'
copyright = u'2014, Sebastian Wiesner'

version = '.'.join(__version__.split('.')[:2])
release = __version__

nitpick_ignore = [
    ('el:function', 'stringp'),
]

linkcheck_ignore = [
    r'^https://help.github.com/.*$', # Gives 404 for whatever reason
]

pygments_style = 'sphinx'

html_theme = 'default'

intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://sphinx-doc.org': None}

emacs_lisp_load_path = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample'))
]

def setup(app):
    app.add_object_type('confval', 'confval',
                        objname='configuration value',
                        indextemplate='pair: %s; configuration value')
