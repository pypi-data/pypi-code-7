# coding=utf-8
from django.conf import settings
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from ..models import FotoramaSlider

register = Library()

@register.inclusion_tag('fotorama/default.html')
def fotorama_slider(name):
    # TODO: Сделать поддержку категорий слайдов
    qs = FotoramaSlider.objects.all()
    return {'slide_list': qs}

@register.simple_tag
@stringfilter
def fotorama_jquery_url():
    return '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

try:
    static_url = settings.STATIC_URL
except:
    static_url = '/static/'


@register.simple_tag
@stringfilter
def fotorama_css():
    # Тег возвращает теги подгрузки css
    _str = '<link rel="stylesheet" href="{}fotorama/css/fotorama.css" />'.format(static_url)
    return mark_safe(_str)


@register.simple_tag
@stringfilter
def fotorama_js():
    # Тег возвращает тег подгрузки js
    _str = '<script type="text/javascript" src="{}fotorama/css/fotorama.css"></script>'.format(static_url)
    return mark_safe(_str)