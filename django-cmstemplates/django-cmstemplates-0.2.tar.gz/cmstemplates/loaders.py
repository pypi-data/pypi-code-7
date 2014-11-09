# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.utils._os import safe_join

from cmstemplates.models import TemplateGroup, Template


class Loader(BaseLoader):
    """
    Loads templates from database or cache by template group name.
    """

    is_usable = True

    def load_template_source(self,
                             template_group_name,
                             template_dirs=None):

        # TODO: remove this meaningless contstraint
        if template_group_name.endswith('.html'):
            raise TemplateDoesNotExist(
                'Template group name can not end with ".html"')

        source = []
        dirs = []

        cache_key = 'cmstemplates:group:%s' % template_group_name
        cached = cache.get(cache_key)
        if cached is not None:
            return cached['source'], cached['dirs']

        # All active templates for a group
        templates = Template.objects.filter(
            group__name=template_group_name,
            is_active=True,
        ).order_by('weight')

        if not templates:
            # If there are no template files and no template group,
            # create a group.
            if not TemplateGroup.objects.filter(name=template_group_name).count():
                TemplateGroup.objects.create(
                    name=template_group_name)
            # If group exist and is empty, save it in cache.
            # Cache will be invalidated after template addition.
            else:
                cache.set(cache_key, {'source': '', 'dirs': ''})

        # Generate template group content
        for f in templates:
            if f.only_for_superuser:
                content = ''.join([
                    u'{% if request.user.is_superuser %}',
                    f.content,
                    u'{% endif %}',
                ])
            else:
                content = f.content
            source.append(content)
            dirs.append('template %s content' % f.id)

        source_text = ''.join(source)
        dirs_text = ''.join(dirs)
        cache.set(cache_key, {'source': source_text, 'dirs': dirs_text})
        return source_text, dirs_text

_loader = Loader()
