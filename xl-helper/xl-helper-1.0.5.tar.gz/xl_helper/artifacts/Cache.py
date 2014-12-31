import os

from os.path import expanduser


class Cache:

    def __init__(self, config):
        self.location = expanduser(config.get("cache", "location"))

    def get(self, dist):

        if not os.path.isdir(self.location):
            print("Creating cache directory %s since it does not exist" % self.location)
            os.makedirs(self.location)
        else:
            print("Using cache at %s" % self.location)

        artifact_location = os.path.join(self.location, dist.get_filename())

        if not os.path.isfile(artifact_location) or "SNAPSHOT" in dist.get_filename():
            dist.download(self.location)
        else:
            print "File %s is already cached." % dist.get_filename()

        return artifact_location