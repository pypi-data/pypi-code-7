#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

extensions = [
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'markey'
copyright = '2014, Christopher Grebs'
version = '0.4'
release = '0.4'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'markeydoc'
latex_documents = [
  ('index', 'markey.tex', 'Markey Documentation',
   'Christopher Grebs', 'manual'),
]
man_pages = [
    ('index', 'markey', 'Markey Documentation',
     ['Christopher Grebs'], 1)
]
texinfo_documents = [
  ('index', 'markey', 'Markey Documentation',
   'Christopher Grebs', 'markey', 'One line description of project.',
   'Miscellaneous'),
]
intersphinx_mapping = {'http://docs.python.org/': None}
