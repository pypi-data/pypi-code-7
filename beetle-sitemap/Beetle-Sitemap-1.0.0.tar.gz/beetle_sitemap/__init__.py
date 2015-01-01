import os
import xml.etree.ElementTree as ET


class BeetleSitemap(object):
    def __init__(self, context, config):
        self.folder = context.config.folders.get('output')
        self.site = config.get('site')
        self.sitemap = None

    def run(self):
        if not self.site:
            print('Beetle-Sitemap need a configuration option "site" to specify where the website is going to be available at. Check the README at https://github.com/Tenzer/beetle-sitemap for more details.')
            return

        self.sitemap = ET.TreeBuilder()
        self.sitemap.start('urlset', {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
        for file_path in self.walk(self.folder):
            self.handle(file_path)

        self.sitemap.end('urlset')
        tree = ET.ElementTree(self.sitemap.close())
        tree.write(os.path.join(self.folder, 'sitemap.xml'), encoding='utf-8', xml_declaration=True)

    def walk(self, folder):
        for root, directories, files in os.walk(folder):
            for directory in directories:
                self.walk(os.path.join(root, directory))

            for filename in files:
                if filename.endswith('.html'):
                    yield os.path.join(root[len(self.folder):], filename)

    def handle(self, path):
        if path == 'index.html':
            path = ''
        elif path.endswith('/index.html'):
            path = path[:-10]

        path = os.path.join(self.site, path.lstrip('/'))

        if len(path) >= 2048:
            print('Ignoring "{}" as the path is too long'.format(path))
            return

        self.sitemap.start('url')
        self.sitemap.start('loc')
        self.sitemap.data(path)
        self.sitemap.end('loc')
        self.sitemap.end('url')


def register(context, plugin_config):
    beetle_sitemap = BeetleSitemap(context, plugin_config)
    context.commander.add('sitemap', beetle_sitemap.run, 'Generate a sitemap.xml file in the output directory')
