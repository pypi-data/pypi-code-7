from docutils.parsers.rst import directives
from mako.lookup import TemplateLookup

from .directives import pygments_directive, DotgraphDirective


class Configuration(object):
    'Holds the defaults for a Build'

    defaults = {
        'pygments_directive': True,
        'dotgraph_directive': True,
        'build': '_build',
        'template_dirs': ['templates'],
        'blogroot': 'blog',
        'blogtemplate': 'blog.html',
        'pages': [],
        'debug': False,
    }

    def __init__(self, config_dict, overrides=None):
        'Handle mapping a dict to required configuration parameters'
        if overrides is None:
            overrides = dict()
        self.config_dict = config_dict
        self.overrides = overrides
        if self.pygments_directive:
            # Render code blocks using pygments
            directives.register_directive('code-block', pygments_directive)
        if self.pygments_directive:
            # Render DOT to SVG
            directives.register_directive('dot-graph', DotgraphDirective)
        if not isinstance(self.template_dirs, list):
            raise TypeError('Misconfigured: `template_dirs` should be a list')
        if not isinstance(self.pages, list):
            raise TypeError('Misconfigured: `pages` should be a list')
        self.config_dict['pages'] = ["{0}.rst".format(path)
                                     for path in config_dict.get('pages', [])]
        self.template_lookup = TemplateLookup(directories=self.template_dirs)

    def __getattr__(self, name):
        'Refer to overrides, passed config or defaults'
        try:
            return self.overrides[name]
        except KeyError:
            try:
                return self.config_dict[name]
            except KeyError:
                try:
                    return self.defaults[name]
                except KeyError:
                    raise KeyError("'{0}' not configured".format(name))

    def setval(self, name, value):
        'Set a configuration value'
        self.config_dict[name] = value
