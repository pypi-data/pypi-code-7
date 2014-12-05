# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ImageScaleVocabulary(object):
    """ Create a vocabulary of image scales available in the site """
    implements(IVocabularyFactory)

    def __call__(self, context):
        properties_tool = getToolByName(self, 'portal_properties')
        imagescales_properties = getattr(properties_tool, 'imaging_properties', None)
        raw_scales = getattr(imagescales_properties, 'allowed_sizes', None)

        image_scales = {}
        for line in raw_scales:
            line = line.strip()
            if line:
                splits = line.split(' ')
                if len(splits) == 2:
                    name = line
                    image_scales[name] = (splits[0], )
        return SimpleVocabulary.fromValues(image_scales)

ImageScaleVocabularyFactory = ImageScaleVocabulary()
