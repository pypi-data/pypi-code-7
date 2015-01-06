import subprocess
import json
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()

@register.simple_tag(takes_context=True)
def script_config(context, obj):
	request = context['request']
	if not hasattr(request, "script_config"):
		setattr(request, "script_config", {})
	request.script_config.update(obj)
	return ''

@register.simple_tag(takes_context=True)
def stylesheet(context, link, media=None):
	request = context['request']
	if not hasattr(request, 'stylesheets'):
		setattr(request, 'stylesheets', [])
	request.stylesheets.append({"link": link, "media": media})
	return ''

@register.simple_tag(takes_context=True)
def script(context, link):
	request = context['request']
	if not hasattr(request, 'scripts'):
		setattr(request, 'scripts', [])
	request.scripts.append({"link":link})
	return ""

@register.simple_tag(takes_context=True)
def script_plain(context, code):
	request = context['request']
	if not hasattr(request, 'scripts'):
		setattr(request, 'scripts', [])
	request.scripts.append(code)
	return ""

@register.simple_tag(takes_context=True)
def stylesheets_output(context):
	request = context['request']
	return mark_safe("".join([
		"<link rel='stylesheet' type='text/css' href='%s'%s />" % (static(s['link']), ' media="%s"' % s['media'] if s['media'] else '')
	    for s in request.stylesheets
	]))

@register.simple_tag(takes_context=True)
def scripts_output(context):
	request = context['request']
	if hasattr(request, 'script_config'):
		request.scripts.append("""(function(){if (window.root === undefined) window.root = {}; if (window.root.config === undefined) window.root.config = {}; var additionalConfig = {config}; for (k in additionalConfig) window.root.config[k] = additionalConfig[k];})();""".format(config=json.dumps(request.script_config)))
	return mark_safe("".join([
		"<script type='text/javascript'>%s</script>" % s if isinstance(s, basestring) else "<script type='text/javascript' src='%s'></script>" % static(s['link'])
	    for s in request.scripts
	]))
