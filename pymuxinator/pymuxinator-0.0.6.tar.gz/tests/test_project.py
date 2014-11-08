import mock

from jinja2 import Template
from pymuxinator import exceptions
from pymuxinator.project import Project
from pymuxinator.window import Window
from tests import FixturedTestCase

class TestSampleProject(FixturedTestCase):
    def setUp(self):
        self.project = Project.from_name('sample')

    def test_has_windows(self):
        self.assertTrue(self.project.has_windows)

    def test_windows(self):
        windows = self.project.windows
        self.assertEqual(len(windows), 9)

        for idx, window in enumerate(windows):
            self.assertTrue(isinstance(window, Window))
            self.assertEqual(window.index, idx)
            self.assertTrue(window.config is not None)
            self.assertTrue(window.project_config, self.project.window_config)

    @mock.patch('pymuxinator.project.Project.base_index', return_value=44, new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.project.Project.name', return_value='name', new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.project.Project.pre_window', return_value='pre', new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.project.Project.root', return_value='root', new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.project.Project.tmux', return_value='ftmux', new_callable=mock.PropertyMock)
    def test_window_config(self, mock_tmux, mock_root, mock_pre, mock_name, mock_base):
        self.assertEqual(self.project.window_config, {
            'name': mock_name.return_value,
            'base_index': mock_base.return_value,
            'pre_window': mock_pre.return_value,
            'root': mock_root.return_value,
            'tmux': mock_tmux.return_value,
        })

    def test_project_name(self):
        self.assertEqual(self.project.name, 'sample')

    @mock.patch('pymuxinator.utils.expand_path', return_value='/home/foo/bar')
    def test_root(self, mock_expand):
        self.assertEqual(self.project.root, '/home/foo/bar')

    def test_pre_window(self):
        self.assertEqual(self.project.pre_window, 'source env/bin/activate')

    @mock.patch('pymuxinator.config.load_template')
    def test_render(self, mock_load_template):
        mock_load_template.return_value = Template('Name: {{ project.name }}')
        self.assertEqual(self.project.render(), 'Name: sample')

    def test_environment(self):
        self.assertEqual(self.project.environment, {
            'FOO': 'bar',
            'BAR': None,
        })

    def test_tmux_command(self):
        self.assertEqual(self.project.tmux_command, 'tmux')

    def test_socket_name(self):
        self.assertEqual(self.project.socket_name, 'foo')

    def test_pre(self):
        self.assertEqual(self.project.pre, 'supervisorctl status my_service')

    def test_tmux_options(self):
        self.assertEqual(self.project.tmux_options, '-f ~/.tmux.testing.conf')

    def test_socket(self):
        self.assertEqual(self.project.socket, '-L foo')

    def test_tmux(self):
        expected = 'tmux -f ~/.tmux.testing.conf -L foo'
        self.assertEqual(self.project.tmux, expected)

    def test_window(self):
        self.assertEqual(self.project.window(1), 'sample:1')
        self.assertEqual(self.project.window('10'), 'sample:10')

    def test_show_tmux_options(self):
        expected = 'tmux -f ~/.tmux.testing.conf -L foo start-server\\; show-option -g'
        self.assertEqual(self.project.show_tmux_options, expected)

    def test_tmux_config(self):
        self.assertTrue(isinstance(self.project.tmux_config, dict))

    @mock.patch('pymuxinator.utils.execute_cmd', return_value='')
    def test_tmux_config_cached(self, mock_call):
        """Test that it doesn't shell out when called more than once"""
        self.project.tmux_config = None

        config = self.project.tmux_config
        config = self.project.tmux_config
        self.assertEqual(mock_call.call_count, 1)

    def test_tmux_config_setter(self):
        config = {'foo': 'bar'}
        self.project.tmux_config = config
        self.assertEqual(self.project.tmux_config, config)

    def test_tmux_base_index(self):
        self.project.tmux_config = {'base-index': 55}
        self.assertEqual(self.project.tmux_base_index, 55)

    def test_tmux_pane_base_index(self):
        self.project.tmux_config = {'pane-base-index': 22}
        self.assertEqual(self.project.tmux_pane_base_index, 22)

    def test_base_index(self):
        self.project.tmux_config = {'base-index': '55'}
        self.assertEqual(self.project.base_index, 55)

    def test_base_index_pane(self):
        self.project.tmux_config = {'pane-base-index': '223'}
        self.assertEqual(self.project.base_index, 223)


class TestCustomTmux(FixturedTestCase):
    def setUp(self):
        self.project = Project.from_name('sample_custom')

    def test_tmux_command(self):
        self.assertEqual(self.project.tmux_command, 'custom')

    def test_pre(self):
        expected = 'foo; bar; baz'
        self.assertEqual(self.project.pre, expected)

    def test_tmux_options(self):
        self.assertEqual(self.project.tmux_options, '')

    def test_socket_path(self):
        self.assertEqual(self.project.socket_path, '/foo/bar')

    def test_socket(self):
        self.assertEqual(self.project.socket, '-S /foo/bar')

    def test_tmux(self):
        expected = 'custom -S /foo/bar'
        self.assertEqual(self.project.tmux, expected)

    def test_show_tmux_options(self):
        expected = 'custom -S /foo/bar start-server\\; show-option -g'
        self.assertEqual(self.project.show_tmux_options, expected)


class TestDefaultSocket(FixturedTestCase):
    def setUp(self):
        self.project = Project.from_name('sample_default_socket')

    def test_tmux(self):
        expected = 'tmux -f ~/.tmux.testing.conf'
        self.assertEqual(self.project.tmux, expected)


class TestValidations(FixturedTestCase):
    def test_no_windows(self):
        with self.assertRaises(exceptions.NoWindowsError):
            project = Project.from_name('windowless')

    def test_invalid_name(self):
        with self.assertRaises(exceptions.NoNameError):
            project = Project.from_name('invalid_name')
