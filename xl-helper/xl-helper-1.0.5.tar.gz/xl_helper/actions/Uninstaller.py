import os.path
import shutil

from xl_helper.Utils import Utils


class Uninstaller:

    def __init__(self):
        pass

    def server(self, version, location):
        server_dir = os.path.join(location, Utils.build_server_dir_name(version))
        if os.path.isdir(server_dir):
            shutil.rmtree(server_dir)
        else:
            print "The server {} hasn\'t been removed as it doesn\'t exist".format(server_dir)

        zip_path = os.path.join(location, Utils.build_server_zip_name(version))
        if os.path.isfile(zip_path):
            os.remove(zip_path)
        else:
            print "Zip file {} hasn\'t been removed as it doesn\'t exist".format(zip_path)

    def plugin(self, name, version, location):
        server_dir = os.path.join(location, Utils.build_server_dir_name(version))
        plugin_path = "{path}/plugins/{name}".format(path=server_dir, name=Utils.build_plugin_name(version, name))

        if os.path.isfile(plugin_path):
            os.remove(plugin_path)
        else:
            print "Plugin {} hasn\'t been removed as it doesn\'t exist".format(plugin_path)
