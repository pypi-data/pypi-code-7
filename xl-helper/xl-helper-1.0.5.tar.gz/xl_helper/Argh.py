from argparse import ArgumentParser
import os


class Argh:

    def __init__(self):
        pass

    @staticmethod
    def create_parser():
        parser = ArgumentParser(description='XL helper')
        parser.add_argument('action', choices=['install', 'upgrade', 'uninstall'], type=str, help='What you want to do.')
        parser.add_argument('subject', choices=['server', 'plugin', 'cli'], type=str, help='What will be affected.')
        parser.add_argument('plugin', metavar='PLUGIN_ID', nargs='?', type=str, help='Plugin id.', default=None)
        parser.add_argument('--version', metavar='VER', type=str, help='Version. No version means latest snapshot.', required=False, default='SNAPSHOT')
        parser.add_argument('--dist', metavar='DIST', type=str, help='Distribution path. Instead of downloading, use the local distribution zip/jar.', required=False, default=None)
        parser.add_argument('--path', metavar='PATH', type=str, help='Path to the server installation.', required=False, default=os.getcwd())
        parser.add_argument('--upgrade-from-path', metavar='PATH', type=str, help='Path to the server installation from which it should upgrade.', required=False, default=None)

        parser.add_argument('-start', type=bool, help='Make sure that server is running after the action.', nargs='?', default=False, const=True)
        return parser
