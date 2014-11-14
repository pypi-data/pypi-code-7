from zope.component import getAdapters, getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from collective.viewlet.pythonscript.interfaces import IViewletResultsRenderer

def PythonScriptsVocabFactory(context):
    """ Vocabulary for potential python scripts lisitng """
    scripts_vocab = getUtility(IVocabularyFactory, name=u'python-scripts')(context)
    scripts_vocab._terms.insert(0, SimpleVocabulary.createTerm('', '', u'None'))
    return scripts_vocab


def ViewletsTemplatesVocabFactory(context):
    """ Vocabulary for potential vielets renderers listing """
    terms = [
        SimpleVocabulary.createTerm(name, name, u'%s (%s)' % (name, adapter.title))
        for name, adapter in getAdapters((context, context.REQUEST), IViewletResultsRenderer)
    ]
    terms.insert(0, SimpleVocabulary.createTerm('', '', u'None'))
    return SimpleVocabulary(terms)