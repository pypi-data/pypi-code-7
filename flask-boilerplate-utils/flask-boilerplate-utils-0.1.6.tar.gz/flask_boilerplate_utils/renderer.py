from flask import render_template_string, Markup

def render_field(field, **kwargs):
    template = """
    {% from '_boilerplate/macros.html' import render_field %}
    {{ render_field(field, **kwargs) }}
    """
    return Markup(render_template_string(template, field=field, kwargs=kwargs))

def csrf_setup(**kwargs):
	template = """
	{% from '_boilerplate/macros.html' import csrf_setup %}
	{{ csrf_setup(**kwargs) }}
	"""
	return Markup(render_template_string(template, kwargs=kwargs))