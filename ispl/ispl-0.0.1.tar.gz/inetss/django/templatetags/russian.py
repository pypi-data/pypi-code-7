# coding: utf-8
from math import floor
from django import template
from django.template import TemplateSyntaxError

register = template.Library()


@register.filter
def russian_pluralize(value, endings):
	value = int(floor(value))  # TODO: для нецелых чисел всегда возвращать второе окончание?
	try:
		endings = endings.split(',')
		if value % 100 in (11, 12, 13, 14):
			return endings[2]
		if value % 10 == 1:
			return endings[0]
		if value % 10 in (2, 3, 4):
			return endings[1]
		else:
			return endings[2]
	except:
		raise TemplateSyntaxError
