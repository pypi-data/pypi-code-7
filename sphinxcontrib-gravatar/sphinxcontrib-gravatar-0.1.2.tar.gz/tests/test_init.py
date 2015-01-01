# -*- coding: utf-8 -*-
"""
    unittest for sphinxcontrib.gravatar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
    unicode_literals
)


class TestSetup(object):

    def _get_target(self):
        from sphinxcontrib.gravatar import setup
        return setup

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_app(self, *args, **kwargs):
        class DummyApp(object):

            nodes = []
            config_values = []
            directives = []

            def add_node(self, node, html, latex):
                self.nodes.append(dict(
                    node=node,
                    html=html,
                    latex=latex,
                ))

            def add_config_value(self, name, default, env):
                self.config_values.append(dict(
                    name=name,
                    default=default,
                    env=env,
                ))

            def add_directive(self, name, directive):
                self.directives.append(dict(
                    name=name,
                    directive=directive,
                ))

        return DummyApp(*args, **kwargs)

    def test_it(self, *args, **kwargs):
        app = self._get_dummy_app()
        self._call_fut(app)
        assert 1 == len(app.nodes)
        assert 9 == len(app.config_values)
        assert 1 == len(app.directives)
