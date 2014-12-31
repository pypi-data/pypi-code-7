# -*- coding: utf-8 -*-
"""
    unittest for sphinxcontrib.gravatar.nodes
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
import mock
import pytest


class TestBuildGravatarImageUrl(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import build_gravatar_image_url
        return build_gravatar_image_url

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_no_option(self):
        expect = "http://www.gravatar.com/avatar/801f4e9ad8c6e220718bf2d256b75957"  # NOQA
        assert expect, self._call_fut('ffk2005@gmail.com', {})

    def test_with_option(self):
        ret = self._call_fut('ffk2005@gmail.com', {
            'size': 10,
            'default': 'http://example.com/monsterid',
            'force_default': True,
            'rating': 'x',
        })
        assert 's=10' in ret
        assert 'r=x' in ret
        assert 'd=http%3A%2F%2Fexample.com%2Fmonsterid' in ret
        assert 'f=y' in ret


class TestBuildGravatarProfileUrl(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import build_gravatar_profile_url
        return build_gravatar_profile_url

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_it(self):
        expect = "http://www.gravatar.com/801f4e9ad8c6e220718bf2d256b75957"
        assert expect == self._call_fut('ffk2005@gmail.com')


class TestGetImageFilename(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import get_image_filename
        return get_image_filename

    def _get_dummy_node(self, *args, **kwargs):
        node = {
            'email': 'ffk2005@gmail.com',
            'options': {}
        }
        node.update(**kwargs)
        return node

    def _get_dummy_html_builder(self, *args, **kwargs):
        class DummyBuilder(object):
            def __init__(self, imgpath, outdir):
                self.imgpath = imgpath
                self.outdir = outdir
        return DummyBuilder(*args, **kwargs)

    def _get_dummy_latex_builder(self, *args, **kwargs):
        class DummyBuilder(object):
            def __init__(self, outdir):
                self.outdir = outdir
        return DummyBuilder(*args, **kwargs)

    def _get_dummy_self(self, *args, **kwargs):
        class DummySelf(object):
            def __init__(self, builder):
                self.builder = builder
        return DummySelf(*args, **kwargs)

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def test_it(self):
        import os
        from tempfile import gettempdir
        tempdir = gettempdir()
        imgpath = os.path.join(tempdir, 'img')
        outdir = os.path.join(tempdir, 'outdir')
        expected_filename = 'gravatar-801f4e9ad8c6e220718bf2d256b75957.png'

        # HTML builder
        dummyself = self._get_dummy_self(
            self._get_dummy_html_builder(imgpath=imgpath, outdir=outdir)
        )
        relfn, outfn = self._call_fut(dummyself, self._get_dummy_node())

        assert os.path.join(imgpath, expected_filename) == relfn
        assert os.path.join(outdir, '_images', expected_filename) == outfn

        # LaTeX builder
        dummyself = self._get_dummy_self(
            self._get_dummy_latex_builder(outdir=outdir)
        )
        relfn, outfn = self._call_fut(dummyself, self._get_dummy_node())
        assert expected_filename == relfn
        assert os.path.join(outdir, expected_filename) == outfn

    def test_prefix(self):
        import os
        from tempfile import gettempdir
        tempdir = gettempdir()
        imgpath = os.path.join(tempdir, 'img')
        outdir = os.path.join(tempdir, 'outdir')
        expected_filename = 'changeprefix-801f4e9ad8c6e220718bf2d256b75957.png'

        dummyself = self._get_dummy_self(
            self._get_dummy_html_builder(imgpath=imgpath, outdir=outdir)
        )
        relfn, outfn = self._call_fut(
            dummyself, self._get_dummy_node(), 'changeprefix')

        assert os.path.join(imgpath, expected_filename) == relfn
        assert os.path.join(outdir, '_images', expected_filename) == outfn

    def test_already_exists_outfn(self):
        import os
        from tempfile import gettempdir
        tempdir = gettempdir()
        imgpath = os.path.join(tempdir, 'img')
        expected_filename = 'gravatar-801f4e9ad8c6e220718bf2d256b75957.png'

        outdir = os.path.join(tempdir, 'outdir')
        outfile = os.path.join(outdir, '_images', expected_filename)
        if os.path.isfile(outfile):
            os.unlink(outfile)

        if not os.path.exists(os.path.join(outdir, '_images')):
            os.makedirs(os.path.join(outdir, '_images'))

        open(outfile, 'a').close()

        dummyself = self._get_dummy_self(
            self._get_dummy_html_builder(imgpath=imgpath, outdir=outdir)
        )
        relfn, outfn = self._call_fut(dummyself, self._get_dummy_node())

        assert os.path.join(imgpath, expected_filename) == relfn
        assert outfile == outfn
        os.unlink(outfile)

    def test_options(self):
        import os
        from tempfile import gettempdir
        tempdir = gettempdir()
        imgpath = os.path.join(tempdir, 'img')
        outdir = os.path.join(tempdir, 'outdir')

        dummyself = self._get_dummy_self(
            self._get_dummy_html_builder(imgpath=imgpath, outdir=outdir)
        )
        relfn, outfn = self._call_fut(
            dummyself,
            self._get_dummy_node(
                options={
                    'dummy1': 'd1',
                    'dummy2': 'd2'
                }
            )
        )
        assert imgpath in relfn
        assert 'gravatar-801f4e9ad8c6e220718bf2d256b75957' in relfn
        assert '-d1' in relfn
        assert '-d2' in relfn

        assert outdir in outfn
        assert '_images' in outfn
        assert 'gravatar-801f4e9ad8c6e220718bf2d256b75957' in outfn
        assert '-d1' in outfn
        assert '-d2' in outfn


class TestSaveGravatrImage(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import save_gravatar_image
        return save_gravatar_image

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        node = {
            'username': 'tell-k',
            'email': 'ffk2005@gmail.com',
            'options': {},
            'force_refresh': False
        }
        node.update(**kwargs)
        return node

    def _get_dummy_file_descriptor(self, *args, **kwargs):
        class DummyFileDescriptor(object):

            def __init__(self, code=200, content=b'dummy'):
                self.code = code
                self.content = content

            def getcode(self):
                return self.code

            def read(self):
                return self.content

        return DummyFileDescriptor(*args, **kwargs)

    def test_it(self):
        import os
        from tempfile import gettempdir
        patch_func = 'sphinxcontrib.gravatar.nodes.urlopen'

        outfn = os.path.join(gettempdir(), "dummyimage.png")
        if os.path.isfile(outfn):
            os.unlink(outfn)

        ret = self._get_dummy_file_descriptor()
        with mock.patch(patch_func, return_value=ret, autospec=True):

            self._call_fut(outfn, self._get_dummy_node())
            with open(outfn) as fp:
                assert 'dummy' == fp.read()

        # image file cache
        ret = self._get_dummy_file_descriptor(content="dummy2")
        with mock.patch(patch_func, return_value=ret, autospec=True):

            self._call_fut(outfn, self._get_dummy_node())
            with open(outfn) as fp:
                assert 'dummy' == fp.read()

        os.unlink(outfn)

    def test_force_refresh(self):
        import os
        from tempfile import gettempdir
        patch_func = 'sphinxcontrib.gravatar.nodes.urlopen'

        outfn = os.path.join(gettempdir(), "dummyimage.png")
        if os.path.isfile(outfn):
            os.unlink(outfn)

        ret = self._get_dummy_file_descriptor()
        with mock.patch(patch_func, return_value=ret, autospec=True):

            self._call_fut(outfn, self._get_dummy_node())
            with open(outfn) as fp:
                assert 'dummy' == fp.read()

        # force refresh
        ret = self._get_dummy_file_descriptor(content=b"dummy2")
        with mock.patch(patch_func, return_value=ret, autospec=True):

            self._call_fut(outfn, self._get_dummy_node(force_refresh=True))
            with open(outfn) as fp:
                assert 'dummy2' == fp.read()

        os.unlink(outfn)

    def test_failed_urlopen(self):
        import os
        from tempfile import gettempdir
        from sphinxcontrib.gravatar.nodes import GravatarError

        outfn = os.path.join(gettempdir(), "dummyimage.png")
        patch_func = 'sphinxcontrib.gravatar.nodes.urlopen'
        ret = self._get_dummy_file_descriptor(code=500)
        with mock.patch(patch_func, return_value=ret, autospec=True):

            with pytest.raises(GravatarError) as e:
                self._call_fut(outfn, self._get_dummy_node())

            try:
                error = e.value.message
            # for python3
            except AttributeError:
                error = e.value.args[0]
            assert "Can't fecth gravatar image for 'tell-k'" == error


@mock.patch('sphinxcontrib.gravatar.nodes.save_gravatar_image', autospec=True)
@mock.patch('sphinxcontrib.gravatar.nodes.get_image_filename',
            return_value=('fname', 'outfn'), autospec=True)
class TestHtmlVisitGravatarImage(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import html_visit_gravatar_image
        return html_visit_gravatar_image

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        node = {
            'email': 'ffk2005@gmail.com',
            'unlink': False,
            'alt': "alttest",
            'target': None,
            'css_class': "css_classtest",
        }
        node.update(**kwargs)
        return node

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    def test_it(self, mock_get_image_filename, mock_save_gravatar_image):
        from docutils import nodes

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node()
        with pytest.raises(nodes.SkipNode):
            self._call_fut(dummyself, dummynode)

        mock_get_image_filename.assert_called_with(dummyself, dummynode)
        mock_save_gravatar_image.assert_called_with('outfn', dummynode)
        assert (
            '<a href="http://www.gravatar.com/'
            '801f4e9ad8c6e220718bf2d256b75957"'
            ' class="gravatar-link"><img src="fname" alt="alttest"'
            ' class="css_classtest" /></a>' ==
            dummyself.body.content[0]
        )

    def test_specify_target(self, mock_get_image_filename,
                            mock_save_gravatar_image):
        from docutils import nodes

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node(target='http://example.com/')
        with pytest.raises(nodes.SkipNode):
            self._call_fut(dummyself, dummynode)

        mock_get_image_filename.assert_called_with(dummyself, dummynode)
        mock_save_gravatar_image.assert_called_with('outfn', dummynode)
        assert (
            '<a href="http://example.com/"'
            ' class="gravatar-link"><img src="fname" alt="alttest"'
            ' class="css_classtest" /></a>' == dummyself.body.content[0]
        )

    def test_unlink(self, mock_get_image_filename,
                    mock_save_gravatar_image):
        from docutils import nodes

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node(unlink=True)
        with pytest.raises(nodes.SkipNode):
            self._call_fut(dummyself, dummynode)

        mock_get_image_filename.assert_called_with(dummyself, dummynode)
        mock_save_gravatar_image.assert_called_with('outfn', dummynode)
        assert (
            '<img src="fname" alt="alttest" class="css_classtest" />'
            == dummyself.body.content[0]
        )


@mock.patch('sphinxcontrib.gravatar.nodes.save_gravatar_image', autospec=True)
class TestLaTeXVisitGravatarImage(object):

    def _get_target(self):
        from sphinxcontrib.gravatar.nodes import latex_visit_gravatar_image
        return latex_visit_gravatar_image

    def _call_fut(self, *args, **kwargs):
        return self._get_target()(*args, **kwargs)

    def _get_dummy_node(self, *args, **kwargs):
        node = {}
        node.update(**kwargs)
        return node

    def _get_dummy_self(self, *args, **kwargs):
        class DummyBody(object):
            content = []

            def append(self, content):
                self.content.append(content)

        class DummySelf(object):
            def __init__(self, body):
                self.body = body
        return DummySelf(DummyBody())

    @mock.patch('sphinxcontrib.gravatar.nodes.get_image_filename',
                return_value=('fname', 'outfn'), autospec=True)
    def test_it(self, mock_get_image_filename, mock_save_gravatar_image):
        from docutils import nodes

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node()
        with pytest.raises(nodes.SkipNode):
            self._call_fut(dummyself, dummynode)

        mock_get_image_filename.assert_called_with(dummyself, dummynode)
        mock_save_gravatar_image.assert_called_with('outfn', dummynode)
        assert '\includegraphics{fname}' == dummyself.body.content[0]

    @mock.patch('sphinxcontrib.gravatar.nodes.get_image_filename',
                return_value=(None, 'outfn'), autospec=True)
    def test_fname_is_none(self, mock_get_image_filename,
                           mock_save_gravatar_image):
        from docutils import nodes

        dummyself = self._get_dummy_self()
        dummynode = self._get_dummy_node()
        with pytest.raises(nodes.SkipNode):
            self._call_fut(dummyself, dummynode)

        mock_get_image_filename.assert_called_with(dummyself, dummynode)
        mock_save_gravatar_image.assert_called_with('outfn', dummynode)
        assert 0 == len(dummyself.body.content)
