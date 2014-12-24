# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from coop_bar import get_version
from coop_bar.bar import CoopBar

register = template.Library()


class CoopBarNode(template.Node):

    def render(self, context):
        request = context.get("request", None)
        commands = CoopBar().get_commands(request, context)
        if commands: #hide admin-bar if nothing to display
            css_classes = CoopBar().get_css_classes(request, context)
            context_dict = {'commands': commands, 'css_classes': css_classes}
            #for var_name in ('article', 'object'):
            #    var = context.get(var_name, None)
            #    context_dict[var_name] = var
            t = get_template("coop_bar.html")
            return t.render(Context(context_dict))
        return u''

@register.tag
def coop_bar(parser, token):
    return CoopBarNode()


class CoopBarHeaderNode(template.Node):
    def render(self, context):
        request = context.get("request", None)
        STATIC_URL = getattr(settings, 'STATIC_URL', '')
        url = u'<link rel="stylesheet" href="{0}css/coop_bar.css?v={1}" type="text/css" />'.format(
            STATIC_URL, get_version())
        headers = [url]
        headers += CoopBar().get_headers(request, context)
        return "\n".join(headers)

@register.tag
def coop_bar_headers(parser, token):
    return CoopBarHeaderNode()

