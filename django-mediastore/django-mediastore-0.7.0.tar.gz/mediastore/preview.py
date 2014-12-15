# -*- coding: utf-8 -*-
import types
from django.db.models.query import QuerySet
from django import template
from .models import Media
from .utils import get_content_types_for_type


def _get_template_names(templates, mediatype):
    # ``templates`` is a single template string
    if isinstance(templates, basestring):
        templates = (templates,)
    templates = list(templates)
    for i, template_name in enumerate(templates):
        try:
            templates[i] = template_name % {
                'mediatype': mediatype,
            }
        except (KeyError, TypeError):
            pass
    return templates


def filter_media(media, limit_type=None):
    if limit_type is None:
        return media
    if hasattr(media, '__iter__'):
        if isinstance(media, QuerySet):
            cts = get_content_types_for_type(limit_type)
            return media.filter(content_type__in=cts)
        return list(filter(lambda o: o.get_media_type() == limit_type, media))


def display_media(obj, context=None, extra_context=None,
        template_name_single=None, template_name_many=None,
        limit_type=None):
    if context is None:
        context = template.Context()
    if isinstance(context, types.DictType):
        context = template.Context(context)
    context.push()
    if extra_context:
        context.update(extra_context)

    template_name_single = template_name_single or 'mediastore/types/%(mediatype)s/display.html'
    template_name_many = template_name_many or 'mediastore/types/%(mediatype)s/display_many.html'

    result = u''

    if isinstance(obj, (QuerySet, types.ListType, types.TupleType)):
        many = True
        obj = filter_media(obj, limit_type=limit_type)
        object_list = [x.object for x in obj]
        if len(object_list) == 0:
            context.pop()
            return u''
        media_type = object_list[0].get_media_type()
        for obj in object_list:
            if obj.get_media_type() != media_type:
                raise ValueError(u'Only media objects with the same type are allowed.')
        context['object_list'] = object_list
        try:
            result = template.loader.render_to_string(
                _get_template_names(template_name_many, media_type)[0],
                context,
            )
        except template.TemplateDoesNotExist:
            result = u''
            for obj in context['object_list']:
                context.push()
                context['object'] = obj
                result += template.loader.render_to_string(
                    _get_template_names(template_name_single, media_type)[0],
                    context,
                )
                context.pop()
    elif isinstance(obj, Media):
        many = False
        context['object'] = obj.object
        media_type = obj.get_media_type()
        result = template.loader.render_to_string(
            _get_template_names(template_name_single, media_type)[0],
            context,
        )

    if extra_context:
        context.pop()
    context.pop()
    return result


def preview_media(*args, **kwargs):
    kwargs['template_name_single'] = 'mediastore/types/%(mediatype)s/preview.html'
    kwargs['template_name_many'] = 'mediastore/types/%(mediatype)s/preview_many.html'
    return display_media(*args, **kwargs)
