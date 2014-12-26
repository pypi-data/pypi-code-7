from os import path

import sass


class BeetleSass(object):
    def __init__(self, config):
        self.output_style = config.get('output_style', 'nested')

    def compile(self, content):
        return sass.compile(string=content, output_style=self.output_style)

    def render(self, content, suggested_path):
        content = self.compile(content.decode('utf-8'))

        file_path, _ = path.splitext(suggested_path)
        return '{}.css'.format(file_path), content.encode('utf-8')


def register(context, plugin_config):
    sass_extensions = ['sass', 'scss']
    beetle_sass = BeetleSass(plugin_config)
    context.content_renderer.add_renderer(sass_extensions, beetle_sass.compile)
    context.includer.add(sass_extensions, beetle_sass.render)
