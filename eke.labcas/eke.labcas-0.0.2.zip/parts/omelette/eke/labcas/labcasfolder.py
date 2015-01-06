# encoding: utf-8
# Copyright 2014 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.labcas import MESSAGE_FACTORY as _
from five import grok
from plone.supermodel import model
from zope import schema
from Acquisition import aq_inner
from eke.knowledge.browser.rdf import RDFIngestException
from plone.dexterity.utils import createContentInContainer
import re, logging, rdflib

# TODO: replace these with well-defined constants in other packages, where available (dc title, type URI)
_datasetIDURI   = rdflib.URIRef('urn:edrn:labcas:DatasetId')
_datasetTypeURI = rdflib.URIRef('urn:edrn:labcas:Dataset')
_titleURI       = rdflib.URIRef('http://purl.org/dc/terms/title')
_typeURI        = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_uploadedByURI  = rdflib.URIRef('urn:edrn:labcas:UploadedBy')

# What we consider valid URL schemes
_protocols = (u'http', u'ftp', u'irc', u'news', u'imap', u'gopher', u'jabber', u'webdav', u'smb', u'fish',
    u'ldap', u'pop3', u'smtp', u'sftp', u'ssh', u'feed', u'file', u'testscheme'
)
_urlRE = re.compile(ur'({})s?://?[^\s\r\n]+'.format(u'|'.join(_protocols)))
def isURL(value):
    u'''Ensure the given ``value`` looks like a URL.'''
    return True if _urlRE.match(value) else False
    
class ILabCASFolder(model.Schema):
    u'''A folder containing LabCAS datasets.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of this folder'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this folder.'),
        required=False,
    )
    rdfDataSource = schema.TextLine(
        title=_(u'RDF Data Source'),
        description=_(u'URL to a source of Resource Description Format data defines the contents of this folder.'),
        required=False,
        constraint=isURL,
    )

class LabCASFolderRDFIngestor(grok.View):
    u'''A "view" that ingests RDF and constructs datasets in a LabCAS Folder.'''
    grok.context(ILabCASFolder)
    grok.name('ingest')
    grok.require('cmf.ManagePortal')
    def _parseRDF(self, graph):
        u'''Parse the statements in graph into a mapping {u→{p→o}} where u is a
        resource URI, p is a predicate URI, and o is a list of objects which
        may be literals or URI references.'''
        statements = {}
        for s, p, o in graph:
            if s not in statements:
                statements[s] = {}
            predicates = statements[s]
            if p not in predicates:
                predicates[p] = []
            predicates[p].append(o)
        return statements
    def update(self, **kwargs):
        super(LabCASFolderRDFIngestor, self).update(**kwargs)
        self.request.set('disable_border', True)
        context = aq_inner(self.context)
        rdfDataSource = kwargs.get('rdfDataSource', None)
        if rdfDataSource is None:
            rdfDataSource = context.rdfDataSource
        if rdfDataSource is None:
            raise RDFIngestException(_(u'This folder has no RDF data source URL.'))
        # Get rid of all existing datasets
        context.manage_delObjects(context.keys())
        # Parse RDF
        graph = rdflib.ConjunctiveGraph()
        graph.parse(rdflib.URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)
        # Create new datasets
        self.createdObjects = []
        for uri, predicates in statements.iteritems():
            typeURI = predicates[_typeURI][0]
            if typeURI != _datasetTypeURI: continue
            title = uploadedBy = datasetID = None
            if _titleURI in predicates:
                title = unicode(predicates[_titleURI][0])
            else:
                continue
            uploadedBy = unicode(predicates[_uploadedByURI][0]) if _uploadedByURI in predicates else None
            datasetID = unicode(predicates[_datasetIDURI][0]) if _datasetIDURI in predicates else None
            obj = createContentInContainer(context, 'eke.labcas.labcasdataset', title=title, uploadedBy=uploadedBy,
                datasetID=datasetID, identifier=unicode(uri))
            self.createdObjects.append(obj)
    def numberDatasets(self):
        return len(self.createdObjects)


