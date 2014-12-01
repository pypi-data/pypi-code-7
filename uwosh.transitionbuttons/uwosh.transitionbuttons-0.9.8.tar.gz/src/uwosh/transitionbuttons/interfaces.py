from z3c.form import interfaces

from zope import schema
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.form.browser.itemswidgets import SelectWidget

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('uwosh.transitionbuttons')

items = [ 
            (u"Upper Left", "upperLeft"),
            (u"Upper Right", "upperRight"),
            (u"Bottom Left", "bottomLeft"),
            (u"Bottom Right", "bottomRight")]

terms = [ SimpleTerm(value=pair[1], token=pair[1], title=pair[0]) for pair in items ]

locationVocabulary = SimpleVocabulary(terms)

class IButtonSettings(Interface):
    """Global settings for the transition button panel. Settings stored in the 
       Plone registry
    """
    SelectWidget._messageNoValue = ("bottomRight", "Default")

    floating = schema.Bool(title=u'Floating button box.',
                                description=u'Enable this option to make the transition button box float statically above the page',
                                required=False,
                                default=True)

    pageElement = schema.TextLine(title=u'Site element.', 
                                default=u'#portal-breadcrumbs',
                                description=u'Enter a CSS selector to attach the button box to. If floating is enabled, this \
                                option does nothing.',
                                required=False,)

    floatLocation = schema.Choice(vocabulary=locationVocabulary,
                                title=u'Floating Location',
                                description=u'The location on screen where the transition button box will float. If floating is \
                                disabled, this option does nothing.',
                                default="bottomRight",
                                required=True)

    floatSpacing = schema.TextLine(title=u'Floating Spacing',
                                description=u'The value (in pixels) of spacing between the button box, and the edge of the screen',
                                default=u"10",
                                required=False)

    EnabledTypes = schema.List(title=_(u"Enable content types."),
                                description=u'The content types that the transition button box should appear on. If no \
                                values are added, it is assumed that all content types are allowed.',
                                value_type=schema.Choice(source=u"plone.app.vocabularies.UserFriendlyTypes"),
                                required=False,)

class IButtonConfigLayer(Interface):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """


