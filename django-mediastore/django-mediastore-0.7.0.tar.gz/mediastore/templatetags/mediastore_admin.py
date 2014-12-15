# -*- coding: utf-8 -*-
from django import template
from mediastore.admin import admin_preview_media
from mediastore.templatetags.mediastore_tags import get_display_media_node, display_media_tag
from mediastore.utils import get_media_types

register = template.Library()


class GetMediaTypesNode(template.Node):
    def __init__(self, as_var, media_types):
        self.as_var = as_var
        self.media_types = media_types

    def render(self, context):
        context[self.as_var] = self.media_types
        return ''


def get_media_types_tag(parser, token):
    '''
    {% get_media_types as mediatypes %}
    '''
    try:
        tag_name, as_, as_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(u'%r expects two arguments.' % tag_name)
    media_types = sorted(get_media_types())
    return GetMediaTypesNode(as_var, media_types)
register.tag('get_media_types', get_media_types_tag)


register.tag('admin_preview_media', display_media_tag(
    get_display_media_node(admin_preview_media)))
