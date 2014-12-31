from xl_helper.Utils import Utils


class DownloadsCliDist:

    def __init__(self, version, config):
        self.version = version
        self._downloadsUsername = config.get('downloads', 'username')
        self._downloadsPassword = config.get('downloads', 'password')

    def download(self, target):
        print "Downloading CLI distribution %s" % self.version

        Utils().download(
            url=Utils.build_url(_version=self.version, _xltype="cli"),
            target=target,
            username=self._downloadsUsername,
            password=self._downloadsPassword
        )

        return self

    def get_filename(self):
        return Utils.build_cli_zip_name(self.version)