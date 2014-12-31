import re
from xl_helper.artifacts.server.ServerDist import ServerDist


class LocalServerDist(ServerDist):

    name_matcher = re.compile('.*-([0-9\.]+(-SNAPSHOT)?)-server\.zip')

    def __init__(self, path):
        self.path = path
        version_matches = self.name_matcher.match(self.get_filename())
        self.version = version_matches.group(1)

    def get_filename(self):
        return self.path.split('/')[-1]
