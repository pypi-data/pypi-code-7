import os.path
import shutil
from zipfile import ZipFile

from xl_helper.Utils import Utils
from Server import Server
from xl_helper.artifacts.Cache import Cache
from xl_helper.artifacts.cli.DownloadsCliDist import DownloadsCliDist
from xl_helper.artifacts.server.LocalServerDist import LocalServerDist


class Installer:

    def __init__(self, config):
        self.cache = Cache(config)
        self.license_location = os.path.expanduser(config.get('license', 'location'))
        self.license_location_3x = os.path.expanduser(config.get('license', 'location_3x'))
        self.config = config

    def server(self, dist, target, upgrade_from_path=None, start=False):

        if upgrade_from_path is not None:
            raise Exception("***DEPRECATED*** Please use \"xl-helper upgrade server\"")

        source = dist.path if isinstance(dist, LocalServerDist) else self.cache.get(dist)

        ZipFile(source, 'r').extractall(target)

        # Copy available plugins
        server_dir = os.path.join(target, '.'.join(dist.get_filename().split('.')[:-1]))

        print "Server has been installed to %s" % server_dir

        for root, dirs, files in os.walk(os.path.join(server_dir, 'available-plugins')):
            for file_ in files:
                print "Copying available plugin %s" % file_
                if file_.endswith('.jar'):
                    shutil.copy(os.path.join(root, file_), os.path.join(server_dir, 'plugins', file_))

        proper_license = self.license_location if (dist.version == 'SNAPSHOT' or int(dist.version[0]) >= 4) else self.license_location_3x

        print "Copying license from %s" % proper_license
        shutil.copy(proper_license, os.path.join(server_dir, 'conf', 'deployit-license.lic'))

        for dirpath, d, file_names in os.walk(target):
            for filename in file_names:
                if filename.endswith(".sh"):
                    os.chmod(dirpath + '/' + filename, 0750)

        if start:
            Server.from_config(config=self.config, home=server_dir).run()

        return server_dir

    def plugin(self, name, version, server_location):
        plugins_path = os.path.join(server_location, 'plugins')

        print "Installing plugin %s into " % plugins_path

        u = Utils.build_url(_version=version, _xltype="plugin", _plugin_short_name=name)

        Utils().download(
            url=u,
            target=plugins_path,
            username=self.config.get('downloads', 'username'),
            password=self.config.get('downloads', 'password')
        )

        server = Server.from_config(config=self.config, home=server_location)

        if server.is_running():
            server.restart()

    def cli(self, version, path):
        ZipFile(self.cache.get(DownloadsCliDist(version, self.config)), 'r').extractall(path)
        return os.path.join(path, Utils.build_cli_dir_name(version))




