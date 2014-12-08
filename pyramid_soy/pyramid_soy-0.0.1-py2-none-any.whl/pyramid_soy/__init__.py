# -*- coding:utf-8 -*-

import os
from soy.tofu import SoyTofu

__author__ = 'winkidney'


class SoyRender(object):
    _cache = {}
    _paths = ['.']

    class TemplateNotFound(ValueError):
        pass

    @classmethod
    def render(cls, template_name, name_space, **data):
        """
        :param template_name: template file name, support python file.
        :type template_name: str or unicode
        :param name_space: closure-template's name space.
        :type name_space: str or unicode
        :param data: keywaord arguments will be passed to soy. Use format `key=value`
            like normal keyword argument.
        :return str or unicode
        """
        for path in cls._paths:
            if os.path.isfile(os.path.join(path, template_name)):
                full_template_name = os.path.join(path, template_name)
                break
        else:
            raise cls.TemplateNotFound("Template [%s] not found!" % template_name)
        tofu_cache = cls._cache.get(full_template_name, None)
        if tofu_cache is None:
            tofu = cls.get_tofu(full_template_name)
            cls._cache[full_template_name] = tofu
        else:
            tofu = tofu_cache
        return tofu.newRenderer(name_space).\
            setData(**data).render()

    @classmethod
    def get_tofu(cls, pyfile):
        return SoyTofu.fromFile(open(pyfile, 'ro'))

    @classmethod
    def add_soy_path(cls, path):
        if os.path.isdir(path):
            cls._paths.append(path)
        else:
            raise ValueError('{path} must a dir'.format(path=path))
    @classmethod
    def add_soy_searchpath(cls, config, path):
        """
        Patch for pyramid directive.
        """
        cls.add_soy_path(path)

    @classmethod
    def reload_all(cls):
        pass

    @classmethod
    def reload_one(cls, name, render_file):
        pass


def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    config.add_directive('add_soy_searchpath', SoyRender.add_soy_searchpath)
    config.add_request_method(SoyRender.render, 'soy_render_tostring')