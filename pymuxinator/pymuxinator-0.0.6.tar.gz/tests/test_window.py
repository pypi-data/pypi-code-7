import mock

from pymuxinator.pane import Pane
from pymuxinator.project import Project
from pymuxinator.window import Window
from tests import FixturedTestCase


class WindowTestCase(FixturedTestCase):
    window_idx = 0

    def setUp(self):
        self.project = Project.from_name('sample')
        self.window = self.project.windows[self.window_idx]


class TestWindow(WindowTestCase):
    def test_name(self):
        self.assertEqual(self.window.name, 'editor')

    def test_layout(self):
        self.assertEqual(self.window.layout, 'main-vertical')

    def test_pre(self):
        expected = 'echo "no pane, no gain!"'
        self.assertEqual(self.window.pre, expected)

    def test_pane_count(self):
        self.assertEqual(self.window.pane_count, 4)

    def test_panes(self):
        panes = self.window.panes
        self.assertEqual(len(panes), 4)

        for idx, pane in enumerate(panes):
            self.assertTrue(isinstance(pane, Pane))
            self.assertEqual(pane.index, idx)
            self.assertTrue(len(pane.commands) > 0)
            self.assertTrue(pane.window_config, self.window.pane_config)

    @mock.patch('pymuxinator.window.Window.pre',
        return_value='fake_pre', new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.window.Window.pane_count',
        return_value=55, new_callable=mock.PropertyMock)
    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_pane_config(self, mock_target, mock_pc, mock_pre):
        self.assertEqual(self.window.pane_config, {
            'index': 0,
            'pre': 'fake_pre',
            'pane_count': 55,
            'tmux_window_target': 'fake_target',
        })

    def test_commands(self):
        self.assertEqual(self.window.commands, None)

    def test_tmux_window_target(self):
        self.assertEqual(self.window.tmux_window_target, 'sample:0')

    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_pre_window_command(self, mock_target):
        self.window.project_config['tmux'] = 'fakemux'
        self.window.project_config['pre_window'] = 'fake_pre'

        expected = 'fakemux send-keys -t fake_target fake_pre C-m'
        self.assertEqual(self.window.tmux_pre_window_command, expected)

    def test_tmux_window_command_prefix(self):
        self.window.project_config['tmux'] = 'fakemux'
        self.window.project_config['name'] = 'fake_name'

        expected = 'fakemux send-keys -t fake_name:0'
        self.assertEqual(self.window.tmux_window_command_prefix, expected)

    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_new_window_command(self, mock_target):
        self.window.project_config['tmux'] = 'fakemux'
        self.window.project_config['root'] = '/fake/root'

        expected = 'fakemux new-window -c /fake/root -t fake_target -n editor'
        self.assertEqual(self.window.tmux_new_window_command, expected)

    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_layout_command(self, mock_target):
        self.window.project_config['tmux'] = 'fakemux'

        expected = 'fakemux select-layout -t fake_target main-vertical'
        self.assertEqual(self.window.tmux_layout_command, expected)

    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_select_first_pane(self, mock_target):
        self.window.project_config['tmux'] = 'fakemux'

        expected = 'fakemux select-pane -t fake_target.0'
        self.assertEqual(self.window.tmux_select_first_pane, expected)


class TestWindowMultiPre(WindowTestCase):
    window_idx = 2

    def test_name(self):
        self.assertEqual(self.window.name, 'split_pane')

    def test_layout(self):
        self.assertEqual(self.window.layout, 'main-horizontal')

    def test_pre(self):
        expected = 'echo "first" && echo "second"'
        self.assertEqual(self.window.pre, expected)

    def test_tmux_window_target(self):
        self.assertEqual(self.window.tmux_window_target, 'sample:2')


class TestWindowListCommands(WindowTestCase):
    window_idx = 1

    def test_commands(self):
        self.assertEqual(self.window.commands, [
            "tmux -f ~/.tmux.testing.conf -L foo send-keys -t sample:1 'git branch' C-m",
            "tmux -f ~/.tmux.testing.conf -L foo send-keys -t sample:1 'git status' C-m",
        ])


class TestWindowStringCommands(WindowTestCase):
    window_idx = 3

    def test_commands(self):
        self.assertEqual(self.window.commands, [
            "tmux -f ~/.tmux.testing.conf -L foo send-keys -t sample:3 'service start wobscale' C-m",
        ])


class TestWindowEmptyStringCommands(WindowTestCase):
    window_idx = 7

    def test_commands(self):
        self.assertEqual(self.window.commands, [])


class TestWindowWithBaseIndex(WindowTestCase):
    window_idx = 1

    def setUp(self):
        super(TestWindowWithBaseIndex, self).setUp()
        self.window.project_config['base_index'] = 55

    def test_tmux_window_target(self):
        self.assertEqual(self.window.tmux_window_target, 'sample:56')

    def test_tmux_window_command_prefix(self):
        self.window.project_config['tmux'] = 'fakemux'
        self.window.project_config['name'] = 'fake_name'

        expected = 'fakemux send-keys -t fake_name:56'
        self.assertEqual(self.window.tmux_window_command_prefix, expected)

    @mock.patch('pymuxinator.window.Window.tmux_window_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_select_first_pane(self, mock_target):
        self.window.project_config['tmux'] = 'fakemux'

        expected = 'fakemux select-pane -t fake_target.55'
        self.assertEqual(self.window.tmux_select_first_pane, expected)