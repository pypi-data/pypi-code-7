from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import directlyProvides
from zope.i18nmessageid import MessageFactory

#from plone.app.theming.utils import isValidThemeDirectory
#from plone.app.theming.utils import getZODBThemes
from plone.app.theming.utils import getAvailableThemes

_ = MessageFactory('zettwerk.mobiletheming')


def ThemeVocabulary(context):
    """ Get a list of all ITheme's available in resource directories and make
    a vocabulary.    """

    themes = getAvailableThemes()

    terms = [SimpleTerm(value=theme.__name__,
            token=theme.__name__,
            title=theme.title) for theme in themes]

    return SimpleVocabulary(terms)

directlyProvides(ThemeVocabulary, IVocabularyFactory)
