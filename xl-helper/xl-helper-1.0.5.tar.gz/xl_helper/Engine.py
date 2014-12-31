from xl_helper.actions.Installer import Installer
from xl_helper.actions.Upgrader import Upgrader
from xl_helper.actions.Uninstaller import Uninstaller
from xl_helper.artifacts.server.RemoteServerDist import RemoteServerDist
from xl_helper.artifacts.server.LocalServerDist import LocalServerDist


class Engine:
    def __init__(self, path, config=None):
        self.path = path
        self.config = config

    def run(self, op, subject, version, distribution_path=None, upgrade_from_path=None, start=False, plugin_name=None):

        if op == 'install':

            installer = Installer(self.config)

            if subject == 'server':
                dist = RemoteServerDist(version, self.config) if distribution_path is None else LocalServerDist(distribution_path)
                installer.server(
                    dist=dist,
                    target=self.path,
                    upgrade_from_path=upgrade_from_path,
                    start=start
                )
            elif subject == 'cli':
                installer.cli(version, self.path)
            elif subject == 'plugin':
                installer.plugin(plugin_name, version, self.path)
            else:
                raise Exception("Unknown subject %s" % subject)
        elif op == 'upgrade':
            if subject == 'server':
                dist = RemoteServerDist(version, self.config) if distribution_path is None else LocalServerDist(distribution_path)
                Upgrader(self.config).upgrade(self.path, dist)
            else:
                raise Exception("Upgrade is supported only for server")
        elif op == 'uninstall':
            uninstaller = Uninstaller()

            if plugin_name is None:
                uninstaller.server(version, self.path)
            else:
                uninstaller.plugin(plugin_name, version, self.path)
