
class SemanticVersion:

    def __init__(self, version):
        version_parts = version.split(".")
        if len(version_parts) < 3:
            raise ValueError("Version '" + version + "' doesn't have a MAJOR.MINOR.PATCH format.")
        self.major = version_parts[0]
        self.minor = version_parts[1]
        self.patch = version_parts[2].split('-')[0]
        self.snapshot = len(version_parts[2].split('-')) > 1

    def less_than(self, other_version):
        if not isinstance(other_version, SemanticVersion):
            raise ValueError("The version '%s' is not of type SemanticVersion." % other_version)

        if self.major != other_version.major:
            return self.major < other_version.major

        if self.minor != other_version.minor:
            return self.minor < other_version.minor

        if self.patch < other_version.patch:
            return True

        return self.snapshot and not other_version.snapshot

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__