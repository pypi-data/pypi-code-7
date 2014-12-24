import os

from htmlmin import Minifier


class BeetleHtmlmin(object):
    def __init__(self, context, config):
        self.folder = context.config.folders.get('output')
        self.config = config
        self.minifier = Minifier(**config.get('args', {}))

    def run(self):
        bytes_saved = 0
        for file_path in self.walk(self.folder):
            bytes_saved += self.minify(file_path)

        print('{} saved by HTML minification'.format(self.human_readable_bytes(bytes_saved)))

    def walk(self, folder):
        for root, directories, files in os.walk(folder):
            for directory in directories:
                self.walk(os.path.join(root, directory))

            for filename in files:
                if filename.endswith('.html'):
                    yield os.path.join(root, filename)

    def minify(self, path):
        contents = open(path, encoding='utf-8').read()
        before = len(contents)
        minified = self.minifier.minify(contents)
        after = len(minified)
        open(path, 'w', encoding='utf-8').write(minified)
        return before - after

    @staticmethod
    def human_readable_bytes(number):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if number < 1024:
                return '{:.1f} {}B'.format(number, unit)
            number /= 1024
        return '{:.1f} YiB'.format(number)


def register(context, plugin_config):
    beetle_htmlmin = BeetleHtmlmin(context, plugin_config)
    context.commander.add('htmlmin', beetle_htmlmin.run, 'Minify HTML files in the output directory')
