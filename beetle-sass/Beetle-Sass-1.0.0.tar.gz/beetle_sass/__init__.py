import sass


def render_sass(raw_content):
    return sass.compile(string=raw_content)


def register(context, plugin_config):
    sass_extensions = ['sass', 'scss']
    context.content_renderer.add_renderer(sass_extensions, render_sass)
