# coding=utf-8
__author__ = 'kohlmannj'

import os
from Ity.Tokenizers import Tokenizer
from Ity.Formatters import Formatter
from jinja2 import Environment, FileSystemLoader
import logging
import json
from webassets import Environment as WebAssetsEnvironment
from webassets import Bundle
from webassets.ext.jinja2 import AssetsExtension
from webassets.script import CommandLineEnvironment

class HTMLFormatter(Formatter):

    def __init__(
            self,
            debug=None,
            template="standalone.html",
            partial_template="partial.html",
            paginated_app_template="paginated.html",
            css_file="styles.css",
            template_root=None,
            portable=False,
            tag_maps_per_page=2000,
            build_webassets=False
    ):
        super(HTMLFormatter, self).__init__(debug)
        self.template_root = template_root
        if self.template_root is None:
            self.template_root = os.path.join(
                os.path.dirname(__file__),
                "templates"
            )
        # Jinja2 Environment initialization
        self.env = Environment(
            loader=FileSystemLoader(searchpath=self.template_root),
            extensions=[
                'jinja2.ext.do',
                'Support.jinja2_htmlcompress.jinja2htmlcompress.HTMLCompress',
                AssetsExtension
            ]
        )
        self.assets_env = WebAssetsEnvironment(
            os.path.join(self.template_root, "standalone"),
            "/standalone"
        )
        self.env.assets_environment = self.assets_env
        # Template Initialization
        self.template = self.env.get_template(template)
        self.partial_template = self.env.get_template(partial_template)
        self.paginated_app_template = self.env.get_template(paginated_app_template)
        self.token_strs_index = Tokenizer.INDEXES["STRS"]
        self.css_file = css_file
        self.css_path = os.path.join(
            self.template_root,
            self.css_file
        )
        self.portable = portable
        self.webassets_env = WebAssetsEnvironment(
            os.path.join(
                self.template_root,
                "standalone"
            )
        )
        self.standalone_js = Bundle(
            'js/jquery-2.0.2.js',
            'js/app.js',
            filters='rjsmin',
            output='standalone.js'
        )
        self.webassets_env.register('standalone_js', self.standalone_js)
        self.tag_maps_per_page = tag_maps_per_page
        # Token string index to output
        self.token_str_to_output_index = -1
        self.token_whitespace_newline_str_to_output_index = 0
        # Build the bundles in the webassets environment.
        if build_webassets:
            self._build_webassets()

    def format(self, tags=None, tokens=None, s=None, partial=False):
        #TODO: add arguments for CSS, document title, etc.
        #TODO: Add optional HTML entity encoding.
        #TODO: Do something better about which token string is output.
        # We probably want case-sensitive strings with decoded HTML entities
        # and removed hyphen breaks, but right now there isn't really a good
        # way to specify that. Maybe add an integer indicating the index of
        # the "best" token_str in the token tuple.
        #TODO: Better error condition/s.
        if (
            (tags is None or tokens is None or s is None)
        ):
            raise ValueError("Not enough valid input data given to format() method.")
        template_to_use = self.template
        if partial:
            template_to_use = self.partial_template
        return template_to_use.render(
            tags=tags,
            tokens=tokens,
            s=s,
            token_strs_index=self.token_strs_index,
            token_type_index=Tokenizer.INDEXES["TYPE"],
            token_types=Tokenizer.TYPES,
            token_str_to_output_index=self.token_str_to_output_index,
            token_whitespace_newline_str_to_output_index=self.token_whitespace_newline_str_to_output_index,
            portable=self.portable
        )

    def format_paginated(self, tags=None, tokens=None, s=None, tag_maps_per_page=None, partial=False, single_file=False, text_name="", text_relative_path="", processing_id="", build_webassets=False):
        # Build the bundles in the webassets environment.
        if build_webassets:
            self._build_webassets()
        if tag_maps_per_page is None:
            tag_maps_per_page = self.tag_maps_per_page
        # First, get the partial formatted output for this content.
        formatted_output = self.format(tags=tags, tokens=tokens, s=s, partial=True)
        pages = []
        total_num_tag_maps = len(tags[1])
        start_index = 1
        while start_index < total_num_tag_maps:
            # Get the end index.
            end_index = start_index + self.tag_maps_per_page
            if end_index > total_num_tag_maps:
                end_index = total_num_tag_maps
            # Get the page.
            pages.append(self._paginate(
                html_content=formatted_output,
                start_tag_map_index=start_index,
                end_tag_map_index=end_index
            ))
            # Increment start_index.
            start_index = end_index + 1
        # Get the paginated application template. There isn't much template to this.
        paginated_app_output = None
        if not partial:
            args = {
                "title": text_name,
                "text_relative_path": text_relative_path,
                "processing_id": processing_id
            }
            if single_file:
                args["tags"] = json.dumps(tags[0])
                args["pages"] = json.dumps(pages)
            paginated_app_output = self.paginated_app_template.render(**args)
        if single_file:
            return paginated_app_output
        else:
            return {
                "app": paginated_app_output,
                "tags": tags[0],
                "pages": pages
            }

    def _build_webassets(self):
        # Set up a logger
        log = logging.getLogger('webassets')
        log.addHandler(logging.StreamHandler())
        log.setLevel(logging.DEBUG)
        cmdenv = CommandLineEnvironment(self.webassets_env, log)
        cmdenv.build()

    def _paginate(self, html_content, start_tag_map_index, end_tag_map_index=None):
        """
        Note: this is quick and dirty, relying on some assumptions about the
        structure of the HTML generated by HTMLFormatter.
        Some untagged text content may be missing! Please be aware that this is
        known to be a naïve solution at best.
        """
        total_num_tag_maps = html_content.count('<span id="tag_')
        # Figure out the index of the last tag map we need.
        if end_tag_map_index is None:
            end_tag_map_index = start_tag_map_index + self.tag_maps_per_page
            if end_tag_map_index > total_num_tag_maps:
                end_tag_map_index = total_num_tag_maps
        # Raise an error if we have been given bad indices.
        if start_tag_map_index < 1 or end_tag_map_index > total_num_tag_maps:
            raise ValueError("Invalid start and/or end tag map indices provided.")
        # Byte position of the starting tag map HTML element.
        start_pos = html_content.find('<span id="tag_' + str(start_tag_map_index) + '"')
        # Byte position of the tag map HTML element **after** the last one we want.
        # (this byte position indicates where the tag map ends.)
        last_pos = html_content.find('<span id="tag_' + str(end_tag_map_index + 1) + '"')
        # If the last_pos is -1, we're attempting to grab more tag maps than there
        # are remaining from the start index. Just use len(html_content) instead.
        if last_pos == -1:
            # Get the last position in the HTML string minus the "</div>" (6 characters) from the end.
            last_pos = len(html_content) - 6
            end_tag_map_index = start_tag_map_index + self.tag_maps_per_page
            if end_tag_map_index > total_num_tag_maps:
                end_tag_map_index = total_num_tag_maps
        # Get the substring of the HTML content.
        partial_html_content = html_content[start_pos:last_pos]
        return partial_html_content
