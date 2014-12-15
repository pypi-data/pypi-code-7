# -*- coding: utf-8 -*-
import os
from django import template
from django.template.defaultfilters import stringfilter
from django_templatequery.template import get_models, filter_models
from mediastore.models import Media
from mediastore.preview import display_media, preview_media
from mediastore.utils import get_media_types

register = template.Library()


def _type(queryset, value):
    return queryset.type(value)

option_callbacks = {
    'type': _type,
}


register.tag('get_media', get_models(Media.objects.all(), option_callbacks))
register.tag('filter_media', filter_models(Media, option_callbacks))


def get_display_media_node(display_func, base_class=None):
    if base_class is None:
        base_class = template.Node
    class DisplayMediaNode(base_class):
        def __init__(self, varname, options, limit_type=None):
            self.limit_type = limit_type
            self.var = template.Variable(varname)
            self.options = options

        def render(self, context):
            obj = self.var.resolve(context)
            return display_func(
                obj,
                context,
                extra_context=self.options,
                limit_type=self.limit_type)
    return DisplayMediaNode


def display_media_tag(node, mediatype=None):
    def display_media(parser, token):
        '''
        {% display_media object size=160px %}
        '''
        tokens = token.split_contents()
        tag_name = tokens[0]
        if len(tokens) < 2:
            raise template.TemplateSyntaxError(u'%r expects at least one arguments.' % tag_name)
        varname = tokens[1]
        options = {}
        if len(tokens) > 2:
            for key, value in [x.split('=') for x in tokens[2].split(',')]:
                options[key] = value
        return node(varname, options, limit_type=mediatype)
    return display_media


class MediaTypeRequirements(template.Node):
    template_name = 'mediastore/types/%s/requirements.html'

    def __init__(self, media_types):
        self.media_types = media_types

    def render(self, context):
        requirements = ''
        for media_type in self.media_types:
            context.push()
            try:
                requirements += template.loader.render_to_string(
                    self.template_name % media_type,
                    context
                )
            except template.TemplateDoesNotExist:
                pass
            context.pop()
        return requirements

    @classmethod
    def tag(cls, parser, token):
        '''
        {% media_requirements swf video set %}
        '''
        tokens = token.split_contents()
        tag_name = tokens[0]
        if len(tokens) < 2:
            raise template.TemplateSyntaxError(u'%r expects at least one arguments.' % tag_name)
        return cls(tokens[1:])


class ListMediaByType(template.Node):
    def __init__(self, queryset, as_var):
        self.queryset = template.Variable(queryset)
        self.as_var = as_var

    def render(self, context):
        queryset = self.queryset.resolve(context)
        if not issubclass(queryset.model, Media) and queryset.model is not Media:
            raise ValueError('You must provide a media queryset.')
        context[self.as_var] = queryset.list_by_type()
        return ''

    @classmethod
    def tag(cls, parser, token):
        '''
        {% list_media_by_type media_queryset as dictionary_of_types %}
        '''
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        if len(tokens) != 3:
            raise template.TemplateSyntaxError(
                '%s needs exactly three arguments.' % tag_name)
        if tokens[1] != 'as':
            raise template.TemplateSyntaxError(
                '%s\'s second argument must be "as".' % tag_name)
        return cls(tokens[0], tokens[2])


register.tag('display_media', display_media_tag(
    get_display_media_node(display_media)))
register.tag('preview_media', display_media_tag(
    get_display_media_node(preview_media)))

# add {% display_media %} tag for every available mediatype
for mediatype in get_media_types():
    register.tag('display_%s' % mediatype,
        display_media_tag(get_display_media_node(display_media), mediatype))
    register.tag('preview_%s' % mediatype,
        display_media_tag(get_display_media_node(preview_media), mediatype))

register.tag('media_requirements', MediaTypeRequirements.tag)
register.tag('list_media_by_type', ListMediaByType.tag)


@register.filter
@stringfilter
def remove_fileextension(value):
    return os.path.splitext(value)[0]


@register.filter
@stringfilter
def get_basename(value):
    return os.path.basename(value)
