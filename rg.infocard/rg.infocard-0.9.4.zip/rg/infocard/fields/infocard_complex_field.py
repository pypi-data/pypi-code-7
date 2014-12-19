# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as __
from z3c.form.object import registerFactoryAdapter
from zope.interface import Interface, implementer
from zope import schema


class IInfocardComplexField(Interface):
    arg_title = schema.TextLine(
        title=__(u"title"),
        default=u"",
        required=True,
    )
    arg_value = schema.Text(
        title=__(u"value"),
        default=u"",
        required=True,
    )
    arg_public = schema.Bool(
        title=__(u"public"),
        default=False,
        required=True,
    )


@implementer(IInfocardComplexField)
class InfocardComplexField(object):

    def __str__(self):
        ''' Return the representation of thi object
        '''
        return repr(self.arg_title, self.arg_value, self.arg_public)


registerFactoryAdapter(IInfocardComplexField, InfocardComplexField)
