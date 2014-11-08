from pymuxinator import utils

class Pane(object):
    def __init__(self, commands, project_config, window_config, index):
        self.commands = commands or []
        self.project_config = project_config
        self.window_config = window_config
        self.index = index

    @property
    def tmux_window_and_pane_target(self):
        project_name = self._get_project_setting('name')
        base_index = self._get_project_setting('base_index')
        window_index = self._get_window_setting('index') + base_index
        pane_index = self.index + base_index

        return u'%s:%i.%i' % (project_name, window_index, pane_index)

    @property
    def tmux_pre_command(self):
        window_pre = self._get_window_setting('pre')

        if window_pre:
            tmux = self._get_project_setting('tmux')
            target = self.tmux_window_and_pane_target

            window_pre = utils.shell_escape(window_pre)
            window_pre = '%s send-keys -t %s %s C-m' % (tmux, target, window_pre,)

        return window_pre or ''

    @property
    def tmux_pre_window_command(self):
        pre = self._get_project_setting('pre_window')

        if pre:
            tmux = self._get_project_setting('tmux')
            target = self.tmux_window_and_pane_target

            pre = utils.shell_escape(pre)
            pre = '%s send-keys -t %s %s C-m' % (tmux, target, pre,)

        return pre or ''

    def tmux_main_command(self, command):
        tmux = self._get_project_setting('tmux')
        project_name = self._get_project_setting('name')

        if command:
            tmux = self._get_project_setting('tmux')
            target = self.tmux_window_and_pane_target

            command = utils.shell_escape(command)
            command = '%s send-keys -t %s %s C-m' % (tmux, target, command,)

        return command or ''

    @property
    def tmux_split_command(self):
        tmux = self._get_project_setting('tmux')
        target = self._get_window_setting('tmux_window_target')

        return '%s splitw -t %s' % (tmux, target,)

    @property
    def is_last(self):
        return self.index == self._get_window_setting('pane_count') - 1

    @property
    def has_multiple_commands(self):
        return self.commands and len(self.commands) > 1

    def _get_project_setting(self, key, default=None):
        return self.project_config.get(key, default)

    def _get_window_setting(self, key, default=None):
        return self.window_config.get(key, default)
