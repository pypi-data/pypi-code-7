from .panels.ajax import AjaxDebugPanel


def includeme(config):
    config.registry.settings['debugtoolbar.panels'].append(AjaxDebugPanel)
    if 'mako.directories' not in config.registry.settings:
        config.registry.settings['mako.directories'] = []
