from django import template

from ..core import JSDir

register = template.Library()


@register.simple_tag
def jsdir(path, **kwargs):
    return JSDir(path, **kwargs).get_tags()
