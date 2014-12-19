# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import TextInput, DateInput, Select, EmailInput
from django.template import Context
from django.template.loader import get_template

from bootstrap3.forms import render_label
from bootstrap3.html import add_css_class
from bootstrap3.renderers import FieldRenderer
from bootstrap3.text import text_value
from .bootstrap3_iconfield import get_bootstrap_iconfield_setting


class IconRenderer(FieldRenderer):
    """
    Renderer to support icons in fields for the bootstrap3 library
    """

    def __init__(self, field, *args, **kwargs):
        super(IconRenderer, self).__init__(field, *args, **kwargs)

        self.widget = field.field.widget

        error_icon_class = kwargs.get('error_icon_class', '')
        help_icon_class = kwargs.get('help_icon_class', '')
        self.custom_icon = kwargs.get('custom-icon',
                                      self.initial_attrs.pop('custom-icon', '')
                                      )
        custom_icon = kwargs.get('custom_icon', '')

        if error_icon_class:
            self.error_icon_class = error_icon_class
        else:
            self.error_icon_class = getattr(
                field.form, 'error_icon_class',
                get_bootstrap_iconfield_setting('error_icon_class'))

        if help_icon_class:
            self.help_icon_class = help_icon_class
        else:
            self.help_icon_class = getattr(
                field.form, 'help_icon_class',
                get_bootstrap_iconfield_setting('help_icon_class'))

    def check_render_icons(self):
        return isinstance(self.widget, (TextInput,
                                        DateInput,
                                        Select,
                                        EmailInput)) and \
            (self.field_help or self.field_errors or self.custom_icon)

    def add_icons(self, html):
        if self.check_render_icons():
            classes = "form-control-feedback "

            if self.field_errors:
                classes += self.error_icon_class
            elif self.custom_icon:
                classes += self.custom_icon
            elif self.field_help:
                classes += self.help_icon_class

            html += '<span class="{klasses}" aria-hidden="true"></span>' \
                .format(klasses=classes)
        return html
    # Return errors and html in different tags

    def append_to_field(self, html):
        help_text = self.field_help
        errors = self.field_errors

        html_errors = get_template(
            'bootstrap3-iconfield/field_errors.html'
        ).render(Context({
            'field': self.field,
            'errors': errors,
            'layout': self.layout,
        }))

        html_help = get_template(
            'bootstrap3-iconfield/field_help.html'
        ).render(Context({
            'field': self.field,
            'help': help_text,
            'layout': self.layout,
        }))

        if help_text:
            html += '<span class="help-block">{help}</span>'.format(
                help=html_help)

        if errors:
            html += '<span class="errors-block">{errors}</span>'.format(
                errors=html_errors)
        return html

    # If there are icons to render we need to add the has-feedback
    # class to add the margin right
    def get_form_group_class(self):
        form_group_class = super(IconRenderer, self).get_form_group_class()

        if self.check_render_icons():
            form_group_class = add_css_class(form_group_class, 'has-feedback')
        return form_group_class

    def render(self):
        # See if we're not excluded
        if self.field.name in self.exclude.replace(' ', '').split(','):
            return ''
        # Hidden input requires no special treatment
        if self.field.is_hidden:
            return text_value(self.field)
        # Render the widget
        self.add_widget_attrs()
        html = self.field.as_widget(attrs=self.widget.attrs)
        self.restore_widget_attrs()
        # Render the icons
        html = self.add_icons(html)
        # Start post render
        html = self.post_widget_render(html)
        html = self.wrap_widget(html)
        html = self.make_input_group(html)
        html = self.append_to_field(html)
        html = self.wrap_field(html)
        html = self.add_label(html)
        html = self.wrap_label_and_field(html)
        return html


class IconHorizontalRenderer(IconRenderer):
    """
    Renderer to support icons in fields for the bootstrap3 library with
    horizontal forms
    """

    def __init__(self, field, *args, **kwargs):
        kwargs['layout'] = 'horizontal'
        super(IconHorizontalRenderer, self).__init__(field, *args, **kwargs)
