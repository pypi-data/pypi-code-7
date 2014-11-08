import mock

from pymuxinator.project import Project
from pymuxinator.window import Window
from tests import FixturedTestCase


class PaneTestCase(FixturedTestCase):
    pane_idx = 0

    def setUp(self):
        self.project = Project.from_name('sample')
        self.window = self.project.windows[0]
        self.pane = self.window.panes[self.pane_idx]


class TestPane(PaneTestCase):
    def test_has_multiple_commands(self):
        self.assertFalse(self.pane.has_multiple_commands)

    def test_tmux_window_and_pane_target(self):
        self.assertEqual(self.pane.tmux_window_and_pane_target, 'sample:0.0')

    @mock.patch('pymuxinator.pane.Pane.tmux_window_and_pane_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_pre_command(self, mock_target):
        self.pane.project_config['tmux'] = 'fakemux'
        self.pane.window_config['pre'] = 'fake_pre'

        expected = 'fakemux send-keys -t fake_target fake_pre C-m'
        self.assertEqual(self.pane.tmux_pre_command, expected)

    @mock.patch('pymuxinator.pane.Pane.tmux_window_and_pane_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_pre_window_command(self, mock_target):
        self.pane.project_config['tmux'] = 'fakemux'
        self.pane.project_config['pre_window'] = 'fake_pre_window'

        expected = 'fakemux send-keys -t fake_target fake_pre_window C-m'
        self.assertEqual(self.pane.tmux_pre_window_command, expected)

    @mock.patch('pymuxinator.pane.Pane.tmux_window_and_pane_target',
        return_value='fake_target', new_callable=mock.PropertyMock)
    def test_tmux_main_command(self, mock_target):
        self.pane.project_config['tmux'] = 'fakemux'

        expected = 'fakemux send-keys -t fake_target hey C-m'
        self.assertEqual(self.pane.tmux_main_command('hey'), expected)

    def test_tmux_split_command(self):
        self.pane.project_config['tmux'] = 'fakemux'
        self.pane.window_config['tmux_window_target'] = 'fake_tar'

        expected = 'fakemux splitw -t fake_tar'
        self.assertEqual(self.pane.tmux_split_command, expected)

    def test_is_last(self):
        self.assertFalse(self.pane.is_last)

class TestPaneMultipleCommands(PaneTestCase):
    pane_idx = 3

    def test_has_multiple_commands(self):
        self.assertTrue(self.pane.has_multiple_commands)

    def test_tmux_window_and_pane_target(self):
        self.assertEqual(self.pane.tmux_window_and_pane_target, 'sample:0.3')


class TestPaneLast(PaneTestCase):
    pane_idx = 3

    def test_is_last(self):
        self.assertTrue(self.pane.is_last)