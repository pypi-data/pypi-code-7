from xl_helper.Utils import Utils
from xl_helper.artifacts.server.ServerDist import ServerDist
from jenkinsapi.jenkins import Jenkins


class RemoteServerDist(ServerDist):

    def __init__(self, version, config):
        self.config = config
        self.version = version
        self._downloadsUsername = self.config.get('downloads', 'username')
        self._downloadsPassword = self.config.get('downloads', 'password')

        if config.has_section('jenkins'):
            self._jobName = self.config.get('jenkins', 'server-job')
            self._jenkins = Jenkins(
                self.config.get('jenkins', 'url'),
                self.config.get('jenkins', 'username'),
                self.config.get('jenkins', 'password'),
                lazy=True
            )
        elif self.version == 'SNAPSHOT':
            raise Exception("Please configure jenkins section in your config file in order to install snapshots.")

    def download(self, target):
        print "Downloading: %s" % self.get_filename()
        username = self._jenkins.username if self.version == 'SNAPSHOT' else self._downloadsUsername
        password = self._jenkins.password if self.version == 'SNAPSHOT' else self._downloadsPassword
        return Utils().download(url=self._get_url(), target=target, username=username, password=password)

    def _get_url(self):

        if self.version == 'SNAPSHOT':
            job = self._jenkins.get_job(self._jobName)
            artifacts = job.get_last_good_build().get_artifact_dict().values()
            server_artifact = [a for a in artifacts if a.filename.endswith('-server.zip')].pop()
            return server_artifact.url
        else:
            return Utils.build_url(_version=self.version, _xltype="server")

    def get_filename(self):
        return self._get_url().split('/')[-1]
