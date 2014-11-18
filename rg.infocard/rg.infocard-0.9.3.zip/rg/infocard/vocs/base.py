# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from base64 import encodestring
from rg.infocard import rg_infocard_logger as logger
from unicodedata import normalize
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
import re

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def slugify(text, delim=u'-'):
    """ ASCII-only slug."""
    result = []
    for word in _punct_re.split(safe_unicode(text.lower())):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def safe_term(value):
    ''' Fix unicode terms using base64 encodestring
    '''
    return SimpleTerm(
        value.encode('utf8'),
        encodestring(value.encode('utf8')).strip(),
        value
    )


class SimpleSafeVocabulary(SimpleVocabulary):
    '''
    Customized Vocabulary
    '''

    _not_found_msg_template = "Vocabulary has no %s"
    _generic_error_msg_template = "Unknown error accessing %s"

    def not_found_msg(self, value):
        '''
        Return this if the message was not found
        '''
        return self._not_found_msg_template % value

    def generic_error_msg(self, value):
        '''
        Generic error message
        '''

    def getSafeTermTitle(self, value, fallback=u"\u2014"):
        '''
        Access a vocabulary and tries to get term by value.
        If it gets it returns the title, otherwise the fallback

        :param value: the key to look for
        :param fallback: the parameter returned if something goes wrong
        '''
        try:
            return self.getTerm(value).title
        except LookupError:
            msg = self.not_found_msg(value)
            logger.warning(msg)
        except:
            msg = self.generic_error_msg(value)
            logger.exception(msg)
        return fallback
