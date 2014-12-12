import codecs

from copy import copy
from importlib import import_module

from five import grok
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import field
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from plone.directives import form

from seantis.people import _
from seantis.people.interfaces import IList
from seantis.people.browser import BaseForm
from seantis.people.errors import ContentExportError
from seantis.people.content.export_content import (
    supported_formats, export_people
)

uppercase_formats = [f.upper() for f in supported_formats]


class IExportFormSchema(form.Schema):

    export_fields = schema.List(
        title=_(u"Fields"),
        description=_(u"Fields to include in the export"),
        required=True,
        value_type=schema.Choice(values=[]),
    )

    export_format = schema.Choice(
        title=_(u"Format"),
        values=uppercase_formats,
        default='CSV'
    )


class ExportForm(BaseForm):

    grok.require('cmf.ModifyPortalContent')
    grok.context(IList)
    grok.name('export')

    ignoreContext = True
    output = None

    def render(self):
        if self.output:
            return self.output
        else:
            return super(ExportForm, self).render()

    @property
    def label(self):
        return _(u"Export ${name}", mapping={
            'name': self.context.title
        })

    @property
    def portal_type(self):
        return self.context.used_type()

    @property
    def portal_type_fields(self):
        result = []

        if self.portal_type:
            schema = self.portal_type.lookupSchema()

            for id, f in field.Fields(schema).items():
                result.append((id, f.field.title))

            module = '.'.join(self.portal_type.klass.split('.')[:-1])
            klass = self.portal_type.klass.split('.')[-1]
            klass = getattr(import_module(module), klass)

            membership_fields = klass().membership_fields
            for id in sorted(membership_fields):
                result.append((id, membership_fields[id]))

        return result

    @property
    def fields(self):
        fields = field.Fields(IExportFormSchema)
        self.prepare_export_fields(fields)
        self.prepare_format_field(fields)
        return fields

    def prepare_export_fields(self, fields):

        vocabulary = SimpleVocabulary(terms=[
            SimpleTerm(id, title=title)
            for id, title in self.portal_type_fields
        ])

        default_values = [i[0] for i in self.portal_type_fields]

        f = fields['export_fields']
        f.field = copy(f.field)

        f.field.value_type.vocabulary = vocabulary
        f.field.default = default_values

        f.widgetFactory = CheckBoxFieldWidget

    def prepare_format_field(self, fields):
        f = fields['export_format']
        f.field = copy(f.field)
        f.widgetFactory = RadioFieldWidget

    @property
    def available_actions(self):
        yield dict(name='export', title=_(u"Export"), css_class='context')
        yield dict(name='cancel', title=_(u"Cancel"))

    def handle_export(self):
        try:
            export_fields = self.parameters.get('export_fields')
            export_fields = [
                (id, title) for id, title
                in self.portal_type_fields
                if id in export_fields
            ]

            dataset = export_people(
                self.request,
                self.context,
                self.portal_type.id,
                export_fields
            )

            format = self.parameters.get('export_format').lower()
            filename = '%s.%s' % (self.context.title, format)
            filename = codecs.utf_8_encode('filename="%s"' % filename)[0]

            output = getattr(dataset, format)

            RESPONSE = self.request.RESPONSE
            RESPONSE.setHeader("Content-disposition", filename)
            RESPONSE.setHeader(
                "Content-Type", "application/%s;charset=utf-8" % format
            )
            RESPONSE.setHeader("Content-Length", len(output))

            self.output = output

        except ContentExportError, e:
            self.raise_action_error(e.translate(self.request))
