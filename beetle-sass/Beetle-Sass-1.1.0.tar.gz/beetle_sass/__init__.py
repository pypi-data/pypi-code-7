from os import path

import sass


def render_sass(raw_content):
    return sass.compile(string=raw_content)


def includer_handler(content, suggested_path):
    content = render_sass(content.decode('utf-8'))
    file_path, _ = path.splitext(suggested_path)
    return '{}.css'.format(file_path), content.encode('utf-8')


def register(context, plugin_config):
    sass_extensions = ['sass', 'scss']
    context.content_renderer.add_renderer(sass_extensions, render_sass)
    context.includer.add(sass_extensions, includer_handler)
