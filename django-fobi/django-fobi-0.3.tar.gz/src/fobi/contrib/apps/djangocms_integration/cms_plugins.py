__title__ = 'fobi.contrib.apps.djangocms_integration.widgets'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('FobiFormWidgetPlugin',)

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from fobi.contrib.apps.djangocms_integration.models import FobiFormWidget


class FobiFormWidgetPlugin(CMSPluginBase):
    model = FobiFormWidget
    name = _("Fobi form")
    render_template = "djangocms_integration/widget.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'object': instance,
            'instance': instance,
            'placeholder': placeholder,
            'rendered_html': '', # TODO
        })
        return context

plugin_pool.register_plugin(FobiFormPlugin)
