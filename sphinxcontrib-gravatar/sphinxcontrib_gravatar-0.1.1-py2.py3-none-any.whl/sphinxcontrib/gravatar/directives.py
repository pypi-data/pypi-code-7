# -*- coding: utf-8 -*-
"""
    sphinxcontrib.gravatar.directives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
    unicode_literals,
)
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive

from sphinxcontrib.gravatar.nodes import gravatar_image


class GravatarDirective(Directive):

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        'size': directives.unchanged,
        'default': directives.unchanged,
        'force_default': directives.flag,
        'unlink': directives.flag,
        'target': directives.unchanged,
        'rating': directives.unchanged,
        'class': directives.unchanged,
        'alt': directives.unchanged,
    }
    node_class = gravatar_image

    def run(self):
        """ build gravatar_image node """

        node = self.node_class('', **self.options)
        self.add_name(node)

        config = self.state.document.settings.env.config

        node['username'] = ''.join(self.arguments)

        user_settings = dict(config.gravatar_users).get(node['username'])
        if not user_settings:
            msg = "You must set '{0}' settings to 'gravatar_users'."
            msg = msg.format(node['username'])
            reporter = self.state.document.reporter
            return [reporter.warning(msg, line=self.lineno)]

        if 'email' not in user_settings:
            msg = "You must set 'email' settings for '{0}'."
            msg = msg.format(node['username'])
            reporter = self.state.document.reporter
            return [reporter.warning(msg, line=self.lineno)]

        node['alt'] = user_settings.get('alt', node['username'])
        if self.options.get('alt'):
            node['alt'] = self.options.get('alt')

        node['email'] = user_settings.get('email')
        gravatar_options = dict(
            size=user_settings.get('size', config.gravatar_default_size),
            rating=user_settings.get('rating', config.gravatar_default_rating),
            default=user_settings.get(
                'default', config.gravatar_default_image),
            force_default=user_settings.get(
                'force_default', config.gravatar_force_default),
        )
        for option in gravatar_options.keys():
            if option in self.options:
                if option == 'force_default':
                    gravatar_options['force_default'] = True
                else:
                    gravatar_options[option] = self.options.get(option)

        node['options'] = gravatar_options

        node['unlink'] = user_settings.get('unlink', config.gravatar_unlink)
        if 'unlink' in self.options:
            node['unlink'] = True

        node['target'] = user_settings.get(
            'target', config.gravatar_default_target)
        if self.options.get('target'):
            node['target'] = self.options.get('target')

        node['css_class'] = user_settings.get(
            'class', config.gravatar_default_class)
        if self.options.get('class'):
            node['css_class'] = self.options.get('class')

        node['force_refresh'] = config.gravatar_force_refresh
        return [node]
