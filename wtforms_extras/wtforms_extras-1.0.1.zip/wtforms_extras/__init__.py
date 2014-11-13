from chameleon import PageTemplateLoader
import os
import logging
from wtforms import validators


logger = logging.getLogger('wtforms_extras')

path = os.path.dirname(__file__)
templates = os.path.join(path, "templates")

template_styles = {
    'default': PageTemplateLoader(os.path.join(templates, "default")),
    'bootstrap': PageTemplateLoader(os.path.join(templates, "bootstrap")),
    'foundation': PageTemplateLoader(os.path.join(templates, "foundation"))
}


def _getLoader(style):
    try:
        template_loader = template_styles[style]
    except KeyError:
        logger.warn('error loading field style %s, loading default' % style)
        template_loader = template_styles['default']
    return template_loader


def _getTemplate(style, *names):
    loader = _getLoader(style)
    template = None
    for name in names:
        try:
            template = loader[name]
            break
        except ValueError:
            pass
    if template is None and style != 'default':
        # try again with default loader
        template = _getTemplate('default', *names)
    return template


try:
    unicode = unicode  # noqa
except NameError:
    # python 3
    unicode = str


class HTML(unicode):
    def __html__(self):
        return self


NO_VALUE = object()


def render_field(form, fieldname, style='default', field_options=NO_VALUE,
                 **options):
    if field_options == NO_VALUE:
        field_options = {}
    field = form._fields[fieldname]
    if hasattr(field, 'template'):
        template = field.template
    elif hasattr(field.widget, 'template'):
        template = field.widget.template
    else:
        fieldtype = field.type.lower()
        template = _getTemplate(style, fieldtype + '.pt', 'default.pt')

    if style == 'bootstrap':
        if 'class' not in field_options:
            field_options['class'] = 'form-control'
    if field.description:
        field_options['placeholder'] = field.description

    options['required'] = False
    for validator in field.validators:
        if type(validator) == validators.Required:
            options['required'] = True
            break

    if template:
        return HTML(template(field=field, field_options=field_options,
                             errors=form.errors.get(fieldname, []),
                             **options))
    else:
        return HTML(field(**field_options))


def render_form(form, style='default', field_options=NO_VALUE, **options):
    if field_options == NO_VALUE:
        field_options = {}
    if hasattr(form, '_order'):
        order = form._order
    else:
        order = form._fields.keys()

    template = _getTemplate(style, 'form.pt')

    def render(fieldname):
        return render_field(form, fieldname, style=style,
                            field_options=field_options.copy(), **options)
    return HTML(template(form=form, fields=order, render=render))


class Renderer(object):

    def __init__(self, form=None, style='default', field_options=NO_VALUE,
                 **options):
        self.style = style
        self.form = form
        self.options = options
        if field_options == NO_VALUE:
            field_options = {}
        self.field_options = field_options

    def __call__(self):
        return render_form(self.form, style=self.style,
                           field_options=self.field_options, **self.options)

    def field(self, fieldname):
        return render_field(self.form, fieldname, style=self.style,
                            field_options=self.field_options.copy(),
                            **self.options)
