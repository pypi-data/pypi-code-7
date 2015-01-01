# -*- coding: utf-8 -*-
"""
    unittest for sphinxcontrib.gravatar.directives
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


class DummyConfig(object):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, name):
        if name in self.kwargs:
            return self.kwargs.get(name)
        return self

    def warning(self, msg, line):
        return dict(msg=msg, line=line)


class TestGravatarDirective(object):

    def _get_target_class(self):
        from sphinxcontrib.gravatar.directives import GravatarDirective
        return GravatarDirective

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def _get_dummy_config(self, **kwargs):
        config = dict(
            gravatar_users=(('tell-k', {'email': 'ffk2005@gmail.com'}),),
            gravatar_default_size=None,
            gravatar_default_rating=None,
            gravatar_default_image=None,
            gravatar_default_class="gravatar",
            gravatar_force_default=False,
            gravatar_force_refresh=False,
            gravatar_unlink=False,
            gravatar_default_target=None,
        )
        config.update(kwargs)
        return DummyConfig(**config)

    def _get_params(self, **kwargs):
        params = dict(
            name='dummyname',
            arguments='tell-k',
            options={},
            content="",
            lineno=1,
            content_offset=1,
            block_text="",
            state="",
            state_machine="",
        )
        params.update(kwargs)
        return params

    def test_it(self):
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config()

        nodes = directive.run()
        node = nodes[0]

        assert 1 == len(nodes)

        assert 'tell-k' == node['username']
        assert 'tell-k' == node['alt']
        assert 'ffk2005@gmail.com' == node['email']
        assert {
            'default': None,
            'rating': None,
            'force_default': False,
            'size': None
        } == node['options']

        assert False is node['unlink']
        assert None is node['target']
        assert 'gravatar' == node['css_class']
        assert False is node['force_refresh']

    def test_invalid_gravatar_users(self):
        directive = self._make_one(**self._get_params())

        # non exists target user.
        directive.state = self._get_dummy_config(
            gravatar_users=()
        )
        nodes = directive.run()
        node = nodes[0]
        assert 1 == len(nodes)

        expect_msg = "You must set 'tell-k' settings to 'gravatar_users'."
        assert expect_msg == node['msg']
        assert 1 == node['line']

        # non exists 'email' of target user.
        directive.state = self._get_dummy_config(
            gravatar_users=(('tell-k', {'dummyopt': 'dummy'}),),
        )
        nodes = directive.run()
        node = nodes[0]
        assert 1 == len(nodes)
        assert "You must set 'email' settings for 'tell-k'." == node['msg']
        assert 1 == node['line']

    def test_option_alt(self):

        # settings for user
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'alt': 'alttext1',
                }),
            ),
        )
        nodes = directive.run()
        node = nodes[0]
        assert 'alttext1' == node['alt']

        # setting directive option
        directive = self._make_one(**self._get_params(options=dict(
            alt='alttext2'
        )))
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'alt': 'alttext1',
                }),
            ),
        )
        nodes = directive.run()
        node = nodes[0]
        assert 'alttext2' == node['alt']

    def test_gravatar_options(self):

        # setting defaults.
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_default_image='mm',
            gravatar_default_rating='pg',
            gravatar_default_size=200,
            gravatar_force_default=True,
        )
        nodes = directive.run()
        node = nodes[0]
        assert {
            'default': 'mm',
            'rating': 'pg',
            'force_default': True,
            'size': 200
        } == node['options']

        # setting for user
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'default': 'monsterid',
                    'force_default': False,
                    'rating': "x",
                    'size': 300,
                }),
            ),
            gravatar_default_image='mm',
            gravatar_default_rating='pg',
            gravatar_default_size=200,
            gravatar_force_default=True,
        )
        nodes = directive.run()
        node = nodes[0]
        assert {
            'default': 'monsterid',
            'rating': 'x',
            'force_default': False,
            'size': 300
        } == node['options']

        # setting directive option
        directive = self._make_one(**self._get_params(options=dict(
            default='retro',
            force_default='',
            rating="r",
            size=400
        )))

        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'default': 'monsterid',
                    'force_default': False,
                    'rating': "x",
                    'size': 300,
                }),
            ),
            gravatar_default_image='mm',
            gravatar_default_rating='pg',
            gravatar_default_size=200,
            gravatar_force_default=True,
        )
        nodes = directive.run()
        node = nodes[0]
        assert {
            'default': 'retro',
            'rating': 'r',
            'force_default': True,
            'size': 400
        } == node['options']

    def test_option_unlink(self):

        # setting defaults
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_unlink=True,
        )
        assert True is directive.run()[0]['unlink']

        # setting user_settings
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'unlink': False,
                }),
            ),
            gravatar_unlink = True,
        )
        assert False is directive.run()[0]['unlink']

        # setting directive option
        directive = self._make_one(**self._get_params(options=dict(
            unlink=True,
        )))
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'unlink': False,
                }),
            ),
            gravatar_unlink=True,
        )
        assert True is directive.run()[0]['unlink']

    def test_option_target(self):
        # setting defaults
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_default_target="target1",
        )
        assert 'target1' == directive.run()[0]['target']

        # setting user_settings
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'target': 'target2',
                }),
            ),
            gravatar_default_target="target1",
        )
        assert 'target2' == directive.run()[0]['target']

        # setting directive option
        directive = self._make_one(**self._get_params(options=dict(
            target='target3',
        )))
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'target': 'target2',
                }),
            ),
            gravatar_default_target="target1",
        )
        assert 'target3' == directive.run()[0]['target']

    def test_option_css_class(self):
        # setting defaults
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_default_class="class1",
        )
        assert 'class1' == directive.run()[0]['css_class']

        # setting user_settings
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'class': 'class2',
                }),
            ),
            gravatar_default_class="class1",
        )
        assert 'class2' == directive.run()[0]['css_class']

        # setting directive option
        directive = self._make_one(**self._get_params(options={
            "class": 'class3',
        }))
        directive.state = self._get_dummy_config(
            gravatar_users=(
                ('tell-k', {
                    'email': 'ffk2005@gmail.com',
                    'class': 'class2',
                }),
            ),
            gravatar_default_class="class1",
        )
        assert 'class3' == directive.run()[0]['css_class']

    def test_force_refresh(self):
        # setting defaults
        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_force_refresh=True,
        )
        assert True is directive.run()[0]['force_refresh']

        directive = self._make_one(**self._get_params())
        directive.state = self._get_dummy_config(
            gravatar_force_refresh=False,
        )
        assert False is directive.run()[0]['force_refresh']
