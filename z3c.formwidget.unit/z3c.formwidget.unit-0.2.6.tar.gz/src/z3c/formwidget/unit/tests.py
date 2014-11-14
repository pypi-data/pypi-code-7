# -*- coding: utf-8 -*-

# python imports
import doctest
import os.path
import unittest

# zope imports
from z3c.form import testing
import z3c.form
import zope.component
import zope.interface
import zope.schema

# local imports
from z3c.formwidget.unit import interfaces, widget


def setUp(test):
    # Setup z3c.form basic setup
    testing.setUp(test)
    testing.setupFormDefaults()
    # Widget setup
    template = os.path.join(os.path.dirname(__file__), 'templates', 'input.pt')
    factory = z3c.form.widget.WidgetTemplateFactory(
        template,
        widget=interfaces.IUnitWidget,
    )
    zope.component.provideAdapter(factory, name='input')
    zope.component.provideAdapter(widget.AreaFieldWidget)
    zope.component.provideAdapter(widget.LengthFieldWidget)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'widget.txt',
            setUp=setUp,
            tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
