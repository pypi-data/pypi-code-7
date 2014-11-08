from pymuxinator import config, exceptions, utils
from pymuxinator.window import Window

class Project(object):
    @classmethod
    def from_name(cls, project_name):
        return cls(config.load(project_name))

    def __init__(self, config):
        # caches
        self._tmux_config = None
        self._windows = []
        self._window_config = None

        self.config = config
        self._validate()

    @property
    def base_index(self):
        base_index = self.tmux_pane_base_index or self.tmux_base_index

        if base_index is not None:
            base_index = int(base_index)

        return base_index

    @property
    def has_windows(self):
        return bool(self._get_config('windows'))

    @property
    def windows(self):
        if not self._windows:
            windows = self._get_config('windows')
            window_config = self.window_config

            if windows:
                self._windows = [Window(window, window_config, idx) for idx, window in enumerate(windows)]

        return self._windows

    @property
    def window_config(self):
        if self._window_config is None:
            self._window_config = {
                'name': self.name,
                'base_index': self.base_index,
                'pre_window': self.pre_window,
                'tmux': self.tmux,
                'root': self.root,
            }

        return self._window_config

    @property
    def name(self):
        name = self._get_config('name')
        return name and utils.shell_escape(name)

    @property
    def root(self):
        root = self._get_config('root')
        return root and utils.shell_escape(utils.expand_path(root))

    @property
    def pre(self):
        pre = self._get_config('pre')

        if isinstance(pre, list):
            pre = '; '.join(pre)

        return pre

    @property
    def pre_window(self):
        return self._get_config('pre_window')

    @property
    def environment(self):
        return self._get_config('environment', {})

    @property
    def tmux_command(self):
        return self._get_config('tmux_command', 'tmux')

    @property
    def tmux_options(self):
        return self._get_config('tmux_options', '').strip()

    @property
    def tmux(self):
        cmd_parts = [self.tmux_command]

        if self.tmux_options:
            cmd_parts.append(self.tmux_options)

        if self.socket:
            cmd_parts.append(self.socket)

        return u' '.join(cmd_parts)

    @property
    def socket_name(self):
        return self._get_config('socket_name')

    @property
    def socket_path(self):
        return self._get_config('socket_path')

    @property
    def socket(self):
        if self.socket_path:
            return u'-S %s' % self.socket_path

        if self.socket_name:
            return u'-L %s' % self.socket_name

    @property
    def show_tmux_options(self):
        return u"%s start-server\\; show-option -g" % self.tmux

    @property
    def tmux_config(self):
        if self._tmux_config is None:
            config = utils.execute_cmd(self.show_tmux_options)
            config = config.split('\n')

            options = {}

            for line in config:
                if line:
                    key, value = line.split(' ', 1)
                    options[key] = value

            self._tmux_config = options

        return self._tmux_config

    @tmux_config.setter
    def tmux_config(self, value):
        self._tmux_config = value

    @property
    def tmux_base_index(self):
        return self.tmux_config.get('base-index')

    @property
    def tmux_pane_base_index(self):
        return self.tmux_config.get('pane-base-index')

    def render(self):
        template = config.load_template('tmux')

        return template.render(
            shell=config.get_env_var('SHELL'),
            project=self,
        )

    def window(self, i):
        return u'%s:%s' % (self.name, str(i))

    def _validate(self):
        if not self.has_windows:
            raise exceptions.NoWindowsError

        if not self.name:
            raise exceptions.NoNameError

    def _get_config(self, key, default=None):
        return self.config.get(key, default)
