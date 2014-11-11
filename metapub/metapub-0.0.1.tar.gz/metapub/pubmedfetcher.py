from __future__ import absolute_import

"""metapub.PubMedFetcher -- tools to deal with NCBI's E-utilities interface to PubMed"""

import grp, logging, os, pprint, sys
import xml.etree.ElementTree as ET

logger = logging.getLogger()

from .pubmedarticle import PubMedArticle
from .utils import get_pmid_for_otherid
from .exceptions import MetaPubError

class Borg:
  _shared_state = {}
  def __init__(self):
    self.__dict__ = self._shared_state

class PubMedFetcher(Borg):
    '''PubMedFetcher (a Borg singleton object)

    An interaction layer for querying via specified method to return PubMedArticle objects.
    
    Currently available methods: eutils

    Basic Usage:

        fetch = PubMedFetcher()
    
    To specify a service method (more coming soon):

        fetch = PubMedFetcher('eutils')

    To return an article by querying the service with a known PMID:

        paper = fetch.article_by_pmid('123456')

    Similar methods exist for returning papers by DOI and PM Central id:

        paper = fetch.article_by_doi('10.1038/ng.379')
        paper = fetch.article_by_pmcid('PMC3458974')
    '''

    def __init__(self, method='eutils'):
        Borg.__init__(self)
        self.method = method

        if method=='eutils':
            import eutils.client as ec
            self.qs = ec.QueryService()
            self.article_by_pmid = self._eutils_article_by_pmid
            self.article_by_pmcid = self._eutils_article_by_pmcid
            self.article_by_doi = self._eutils_article_by_doi

        else:
            raise NotImplementedError('coming soon: fetch from local pubmed index.')

    def _eutils_article_by_pmid(self, pmid):
        return PubMedArticle(self.qs.efetch(args={'db': 'pubmed', 'id': pmid } ))

    def _eutils_article_by_pmcid(self, pmcid):
        pmid = get_pmid_for_otherid(pmcid)
        if pmid is None:
            raise MetaPubError('No PMID available for PubMedCentral id %s' % pmcid)
        return self._eutils_article_by_pmid(pmid)
    
    def _eutils_article_by_doi(self, doi):
        pmid = get_pmid_for_otherid(doi)
        if pmid is None:
            raise MetaPubError('No PMID available for doi %s' % doi)
        return self._eutils_article_by_pmid(pmid)

