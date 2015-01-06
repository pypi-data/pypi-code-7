# encoding: utf-8
# Copyright 2014 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.labcas import MESSAGE_FACTORY as _
from five import grok
from plone.supermodel import model
from zope import schema

class ILabCASDataset(model.Schema):
    u'''A data set stored in LabCAS.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of this dataset.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this dataset.'),
        required=False,
    )
    identifier = schema.TextLine(
        title=_(u'Identifier'),
        description=_(u'Unique RDF URI that identifies this resource. Conventionally, this is a URL into LabCAS.'),
        required=True,
    )
    uploader = schema.TextLine(
        title=_(u'Uploaded By'),
        description=_(u'User name of the person who uploaded this dataset.'),
        required=False,
    )
    datasetID = schema.TextLine(
        title=_(u'Dataset ID'),
        description=_(u'Dataset identifier, which is somehow different from the RDF identifier.'),
        required=False,
    )
