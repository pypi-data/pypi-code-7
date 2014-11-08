from pymuxinator import utils
from pymuxinator.pane import Pane

class Window(object):
    def __init__(self, config, project_config, index):
        self.config = config
        self.project_config = project_config
        self.index = index

        # readonly caches
        self._layout = None
        self._pre = None
        self._pane_count = 0
        self._panes = None
        self._commands = None

        self._build_window()

    @property
    def name(self):
        keys = self.config.keys()
        return len(keys) and utils.shell_escape(keys[0])

    @property
    def layout(self):
        return self._layout

    @property
    def pre(self):
        pre = self._pre

        if isinstance(pre, list):
            pre = [x for x in pre if x]
            pre = ' && '.join(pre)

        return pre or ''

    @property
    def pane_count(self):
        return self._pane_count

    @property
    def panes(self):
        return self._panes

    @property
    def pane_config(self):
        return {
            'index': self.index,
            'pre': self.pre,
            'pane_count': self.pane_count,
            'tmux_window_target': self.tmux_window_target,
        }

    @property
    def commands(self):
        return self._commands

    @property
    def tmux_window_target(self):
        name = self._get_project_setting('name')
        base_index = self._get_project_setting('base_index')

        return u"%s:%i" % (name, self.index + base_index)

    @property
    def tmux_pre_window_command(self):
        pre_window = self._get_project_setting('pre_window')

        if pre_window:
            tmux = self._get_project_setting('tmux')
            window_target = self.tmux_window_target

            pre_window = utils.shell_escape(pre_window)
            pre_window = '%s send-keys -t %s %s C-m' % (tmux, window_target, pre_window,)

        return pre_window or ''

    @property
    def tmux_window_command_prefix(self):
        tmux = self._get_project_setting('tmux')
        name = self._get_project_setting('name')
        index = self.index + self._get_project_setting('base_index')

        return u'%s send-keys -t %s:%i' % (tmux, name, index)

    @property
    def tmux_new_window_command(self):
        tmux = self._get_project_setting('tmux')
        window_target = self.tmux_window_target
        path = self._get_project_setting('root')

        if path:
            path = u'-c %s' % path

        return u'%s new-window %s -t %s -n %s' % (tmux, path, window_target, self.name,)

    @property
    def tmux_layout_command(self):
        tmux = self._get_project_setting('tmux')
        window_target = self.tmux_window_target

        return '%s select-layout -t %s %s' % (tmux, window_target, self.layout,)

    @property
    def tmux_select_first_pane(self):
        tmux = self._get_project_setting('tmux')
        window_target = self.tmux_window_target
        index = self._get_project_setting('base_index') # + self.panes[0].index

        return '%s select-pane -t %s.%i' % (tmux, window_target, index)

    def _build_window(self):
        window_value = self.config.values()[0]

        if isinstance(window_value, dict):
            layout = window_value.get('layout')
            self._layout = layout and utils.shell_escape(layout)

            self._pre = window_value.get('pre')
            self._pane_count = len(window_value.get('panes'))
            self._panes = self._build_panes(window_value.get('panes'))
        else:
            self._commands = self._build_commands(window_value)
            pass

    def _build_panes(self, pane_config):
        panes = []

        for idx, pane in enumerate(pane_config):
            if isinstance(pane, dict):
                commands = pane.values()[0]
            else:
                commands = [pane]

            panes.append(Pane(commands, self.project_config, self.pane_config, idx))

        return panes

    def _build_commands(self, window_value):
        pref = self.tmux_window_command_prefix

        if isinstance(window_value, list):
            return [
                '%s %s C-m' % (pref, utils.shell_escape(command))
                for command in window_value if command
            ]

        if isinstance(window_value, str) and window_value:
            return ['%s %s C-m' % (pref, utils.shell_escape(window_value))]

        return []

    def _get_project_setting(self, key, default=None):
        return self.project_config.get(key, default)
