#!/usr/bin/env python3

import sys
import os
from eclaircie import *


# -- Options specific to éClaircie ----------------------------------------------

html_theme_options = {}

# The languages supported by the website, and the corresponding languages.
# The values belows setup a website, with:
#  * a French version (in which English-only documents are shown in English)
#  * an English version (in which French-only documents are hidden)

langs = [
    Language("Français", "fr_FR.utf8", "fr", "en"),
    Language("English",  "en_US.utf8", "en"),
]

.. lang:: fr

language = "fr"
html_theme_options["show_eclaircie"] = """Propulsé par <a href="http://lesfleursdunormal.fr/static/informatique/eclaircie/index_fr.html">éClaircie</a>, le moteur de blog statique et sans nuage !"""

.. lang:: en

language = "en"

.. lang:: all


# The number of recent posts displayed per page

number_of_recent_post = 5

# The default theme.
# Per-category themes can be specified in themes.conf

html_theme = 'green_roses'

# General information about the project.
# Note: you can use '.. lang::' directive here if you want a language-dependent website's title

project      = 'éClaircie' # This is the website's title
author       = 'Jean-Baptiste "Jiba" Lamy'
author_email = "your@email.here"
copyright    = '2014, %s' % author
url          = "http://xxx.org" # This is the final address of the website, online

# Translation strings ; you may want to personalize them or to add additional languages.

ec_translations = {
  ("fr", "older_posts") : "< messages plus anciens",
  ("en", "older_posts") : "< older entries",
  ("fr", "newer_posts") : "messages plus récents >",
  ("en", "newer_posts") : "newer entries >",
  ("fr", "in_category") : "dans",
  ("en", "in_category") : "in",
  ("fr", "more") : "(Suite et commentaires...)",
  ("en", "more") : "(More and comments...)",
  ("fr", "comment") : "(Voir les commentaires...)",
  ("en", "comment") : "(View comments...)",
  ("fr", "comment_title") : "Commentaires",
  ("en", "comment_title") : "Comments",
  ("fr", "add_comment") : "(Ajouter un commentaire - par mail, protège votre vie privée !)",
  ("en", "add_comment") : "(Add a comment - by mail, protect your privacy!)",
  ("fr", "comment_by") : "**Commentaire de %s** (%s)",
  ("en", "comment_by") : "**Comment by %s** (%s)",
}

# The mail directory where comments mails are located.
# When receiving mails, comment mails can be detected with their "To" header (which starts with the
# website name, i.e. the value of the 'project' option above). They should be moved into a specific folder.
# 
# Set to None to disable comments by mail.

comments_mail_dir = "/home/jiba/mail/blog_comments"
#comments_mail_dir = None

# Maximum size for miniature in image gallery

gallery_miniature_width  = 200
gallery_miniature_height = 150

# Maximum size when importing images in an image gallery (i.e. for images not already located in /_images/)
# Bigger image will be reduced

gallery_import_width     = 1400
gallery_import_height    = 1050


# The following set can be used to tag some categories as "special" and make then not propagate
# their post to the parent caegory.
# Note: the values must be "full" category name, including "/index" at the end,
# for example: "informatique/eclaircie/example_site/index"

ec_dont_propagate_posts_for_categories = set()


# -- éClaircie auto-generated options ----------------------------------------------

if len(langs) > 1:
  html_file_suffix = "_%s.html" % language
else:
  html_file_suffix = ".html"


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'eclaircie.sphinx_ext',
]



# -- Other Sphinx options ----------------------------------------------


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

source_suffix = '.rst'

html_add_permalinks = ""

# The short X.Y version.
version = '0.1'
# The full version, including alpha/beta/rc tags.
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

#rst_prolog = """
#.. role:: raw-html(raw)
#   :format: html
#"""

# -- Options for HTML output ----------------------------------------------

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [EC_THEME_PATH]

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    '**': ['globaltoc.html', 'searchbox.html', "email.html"],
}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
html_use_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# Example configuration for intersphinx: refer to the Python standard library.
#intersphinx_mapping = {'http://docs.python.org/': None}
intersphinx_mapping = {}

#autodoc_member_order = "groupwise"
autodoc_member_order  = "bysource"
#autodoc_default_flags = ["show-inheritance", "inherited-members"]


