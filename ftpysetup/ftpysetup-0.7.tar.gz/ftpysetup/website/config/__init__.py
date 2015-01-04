#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""
StoryBox HTML5 writer for DocUtils.

The output conforms to the XHTML option of HTML 5. The CSS2 style sheet
must be available as `http://www.storybox.com/css/style-2010.css` for
proper viewing.
"""
__docformat__ = 'reStructuredText'

import sys
import os
import os.path
import re
from datetime import datetime, timedelta
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import html4css1

class XXWriter(html4css1.Writer):

	default_stylesheet = 'html5css2.css'

	default_stylesheet_path = utils.relative_path(
		os.path.join(os.getcwd(), 'dummy'),
		os.path.join(os.path.dirname(__file__), default_stylesheet))

	default_template = 'template.html'

	default_template_path = utils.relative_path(
		os.path.join(os.getcwd(), 'dummy'),
		os.path.join(os.path.dirname(__file__), default_template))

	settings_spec = html4css1.Writer.settings_spec + (
		'PEP/HTML-Specific Options',
		'For the PEP/HTML writer, the default value for the --stylesheet-path '
		'option is "%s", and the default value for --template is "%s". '
		'See HTML-Specific Options above.'
		% (default_stylesheet_path, default_template_path),
		(('Python\'s home URL.  Default is "http://python.org".',
		  ['--python-home'],
		  {'default': 'http://python.org', 'metavar': '<URL>'}),
		 ('Home URL prefix for PEPs.  Default is "." (current directory).',
		  ['--pep-home'],
		  {'default': '.', 'metavar': '<URL>'}),
		 # For testing.
		 (frontend.SUPPRESS_HELP,
		  ['--no-random'],
		  {'action': 'store_true', 'validator': frontend.validate_boolean}),))

	settings_default_overrides = {
			'input_encoding':'utf-8',
			'output_encoding':'UTF-8',
			'language_code':'en',
			'embed_stylesheet':False,
			'link-stylesheet':True,
			'stylesheet_path':None, #default_stylesheet_path,
			'template':default_template_path
		}

	relative_path_settings = (html4css1.Writer.relative_path_settings + ('template',))
	config_section = 'pep_html writer'
	config_section_dependencies = ('writers', 'html4css1 writer')

	def __init__(self, webroot="http://www.storybox.com", debug=False):
		super().__init__()
		self.webroot = webroot
		self.debug = debug
		self.translator_class = HTMLTranslator

	def apply_template(self):
		self.visitor.layout()
		return super().apply_template()

	def interpolation_dict(self):
		subs = super().interpolation_dict()
		subs["webroot"] = self.webroot
		subs["iso639"] = self.visitor.iso639
		if not self.debug:
			subs["debug_html"] = ""
			subs["debug_jpg"] = ""
			subs["debug_png"] = ""
			subs["debug_gif"] = ""
		else:
			subs["debug_html"] = ".html"
			subs["debug_jpg"] = ".jpg"
			subs["debug_png"] = ".png"
			subs["debug_gif"] = ".gif"
		return subs

	def assemble_parts(self):
		super().assemble_parts()


class HTMLTranslator(html4css1.HTMLTranslator):
	"""
	"""
	def __init__(self, document):
		super().__init__(document)
		self.iso639 = self.settings.language_code

		now = datetime.utcnow()
		now = now - timedelta(microseconds=now.microsecond)
		expire = now + timedelta(days=7)
		metadate = """<meta content="{0}Z" name="date" />""".format(now.isoformat())
		metaexp = """<meta content="{0}Z" http-equiv="expires" />""".format(expire.isoformat())
		self.meta.append(metadate)
		self.meta.append(metaexp)

	#def depart_field_list(self, node):
	#	html4css1.HTMLTranslator.depart_field_list(self, node)
	#	if 'rfc2822' in node['classes']:
	#		 self.body.append('<hr />\n')

	def layout(self, indent='    '):
		"""This will indent each new tag in the body by given number of spaces."""


		self.__indent(self.head, indent)
		self.__indent(self.meta, indent)
		self.__indent(self.stylesheet, indent)
		self.__indent(self.header, indent)
		self.__indent(self.body, indent, initial=3)
		self.__indent(self.footer, indent)
		self.__indent(self.body_pre_docinfo, indent, initial=3)
		self.__indent(self.docinfo, indent)

	def __indent(self, lines, indent, initial=2):
		"""This will indent the given set of lines by normal HTML layout.
		An initial indent of `2*indent` will be used to account for the
		`<html><head>` or `<html><body>` levels."""
		tagempty = re.compile(r"""<\w+(\s+[^>]*?)*/>""")
		tagopen = re.compile(r"""<\w+(\s+[^>]*?)*>""")
		tagclose = re.compile(r"""</\w+\s*>""")
		prefix = indent * initial
		for i in range(len(lines)):
			line = lines[i].strip()
			if tagempty.match(line):
				line = prefix + line
			elif tagopen.match(line):
				line = prefix + line
				prefix = prefix + indent
			elif tagclose.match(line):
				prefix = prefix[:-len(indent)]
				line = prefix + line
			elif '\n' in line:
				line = [prefix + l.strip() for l in line.split('\n')]
				line = os.linesep.join(line)
			else:
				line = prefix + line
			lines[i] = line + os.linesep


