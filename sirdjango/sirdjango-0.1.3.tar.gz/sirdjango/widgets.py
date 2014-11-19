from __future__ import absolute_import, print_function, unicode_literals

import json

from django.forms import widgets
from django.forms.widgets import flatatt
from django.utils.html import mark_safe, format_html

from .conf import settings


class SirTrevorWidget(widgets.Textarea):

    script_template = '<script>new SirTrevor.Editor({options});</script>'

    def __init__(self, blocks=None, extra_options={}, **kwargs):
        super(SirTrevorWidget, self).__init__(**kwargs)
        self.blocks = list(blocks)
        self.extra_options = extra_options

    @property
    def media(self):
        media = widgets.Media(**settings.SIRDJANGO_MEDIA)
        for block in self.blocks:
            media += block.media
        return media

    def render(self, name, value, attrs=None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        final_attrs = self.build_attrs(attrs, name=name)
        textarea = format_html('<textarea{0}>{1}</textarea>',
                               flatatt(final_attrs), value)

        id_ = final_attrs.get('id', None)
        if id_ is None:
            return textarea

        return mark_safe(textarea + self.script_template.format(
            options=self.get_options('#' + id_)))

    def get_options(self, element_selector):
        options = {
            'blockTypes': [block.name for block in self.blocks],
        }
        options.update(self.extra_options)
        # Unforunately, the 'el' option is not valid JSON, but the rest of the
        # options are. Ignore the handcrafted JSON, you saw nothing!
        return '{{el:$({element_selector}), {options}}}'.format(
            element_selector=json.dumps(element_selector),
            options=json.dumps(options)[1:-1])
