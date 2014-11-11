import re

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    """Tag  provide active class for menu elements"""
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''