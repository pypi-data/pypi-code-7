class PluginsSelection:

    def __init__(self, plugins):
        self.plugins = plugins

    # If there are plugins with same names, this method
    # will return those which have lower versions
    def get_outdated_plugins(self):
        outdated = []
        for p in self.plugins:
            old_plugin = self._get_older_version_of_plugin(p)
            if old_plugin is not None and old_plugin not in outdated:
                outdated.append(old_plugin)
        return outdated

    def _get_older_version_of_plugin(self, plugin):
        namesakes = filter(lambda p: p.get_short_name() == plugin.get_short_name(), self.plugins)
        for older_candidate in namesakes:
            if older_candidate.get_sem_version().less_than(plugin.get_sem_version()):
                return older_candidate
        return None