import re

from xl_helper.artifacts.SemanticVersion import SemanticVersion


class Plugin:

    plugin_name_matcher = re.compile('.*\-(plugin|extension)\-([0-9\.]+(-SNAPSHOT)?)(\.jar|-xlPlugin\.xldp)')

    @staticmethod
    def is_plugin(path):
        return Plugin.plugin_name_matcher.match(path) is not None

    def __init__(self, filename):
        self.filename = filename

    def get_short_name(self):
        return self.filename.split("-plugin-")[0]

    def get_version(self):
        version_matches = self.plugin_name_matcher.match(self.filename)
        return version_matches.group(2)

    def get_sem_version(self):
        return SemanticVersion(self.get_version())

    def has_same_name_as(self, another_plugin):
        return self.get_short_name() == another_plugin.get_short_name()

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__