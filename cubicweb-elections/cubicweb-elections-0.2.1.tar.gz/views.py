# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-elections views/forms/actions/components for web ui"""
from logilab.common.decorators import monkeypatch

from cubicweb.predicates import match_user_groups, nonempty_rset, multi_lines_rset
from cubicweb.web import uicfg
from cubicweb.selectors import is_instance
from cubicweb.web import facet
from cubicweb.entities import AnyEntity
from cubicweb.web.views.baseviews import EntityView
from cubicweb.web.views.tableview import TableLayout
from cubicweb.web.views.startup import IndexView
from cubicweb.web.views.basecomponents import RQLInputForm
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.web.action import Action


### OPTIMISATION ##############################################################
# Always make RQL input form visible for the main page
RQLInputForm.visible = True
# Avoid empty left column for anon
BookmarksBox.__select__ = BookmarksBox.__select__ & match_user_groups('users', 'managers')
# Change AnyEntity fetch_attrs to remove the "modification_date" order, as for now
# we have"Any X,AA ORDERBY AA DESC WHERE X is [etype], X modification_date AA
# and is time consuming on the etype list view
AnyEntity.fetch_attrs = ()


### UICFG #####################################################################
pvs = uicfg.primaryview_section
pv_ctl = uicfg.primaryview_display_ctrl

# Tour
pvs.tag_subject_of(('Tour', 'scrutin', 'Scrutin'), 'attributes')
pvs.tag_object_of(('*', 'tour', 'Tour'), 'hidden')
### XXX Costly pvs.tag_object_of(('Candidature', 'tour', 'Tour'), 'relations')
### XXX Costly pv_ctl.tag_object_of(('Candidature', 'tour', 'Tour'), {'vid': 'table'})
# Scrutin
pvs.tag_object_of(('*', 'scrutin', 'Scrutin'), 'hidden')
### XXX Costly pvs.tag_object_of(('Candidature', 'scrutin', 'Scrutin'), 'relations')
### XXX Costly pv_ctl.tag_object_of(('Candidature', 'scrutin', 'Scrutin'), {'vid': 'table'})
# Resultat
pvs.tag_subject_of(('Resultat', 'circonscription', 'Circonscription'), 'attributes')
pvs.tag_subject_of(('Resultat', 'departement', 'Departement'), 'attributes')
# Candidat
pvs.tag_object_of(('Candidature', 'candidat', 'Candidat'), 'relations')
pv_ctl.tag_object_of(('Candidature', 'candidat', 'Candidat'), {'vid': 'table'})
# Liste
pvs.tag_subject_of(('Liste', 'commune', 'Commune'), 'attributes')
pvs.tag_object_of(('Candidature', 'liste', 'Liste'), 'relations')
pv_ctl.tag_object_of(('Candidature', 'liste', 'Liste'), {'vid': 'table'})
# Etiquette
pvs.tag_object_of(('Candidature', 'etiquette', 'Etiquette'), 'relations')
pv_ctl.tag_object_of(('Candidature', 'etiquette', 'Etiquette'), {'vid': 'table'})
# Candidature
pvs.tag_subject_of(('Candidature', 'scrutin', 'Scrutin'), 'attributes')
pvs.tag_subject_of(('Candidature', 'candidat', 'Candidat'), 'attributes')
pvs.tag_subject_of(('Candidature', 'circonscription', 'Circonscription'), 'attributes')
pvs.tag_subject_of(('Candidature', 'liste', 'Liste'), 'attributes')
pvs.tag_subject_of(('Candidature', 'etiquette', 'Etiquette'), 'attributes')
pvs.tag_object_of(('Resultat', 'candidature', 'Candidature'), 'relations')
pv_ctl.tag_object_of(('Resultat', 'candidature', 'Candidature'),
                     {'vid': 'table', 'limit': None})
# Departement
pvs.tag_object_of(('Commune', 'in_departement', 'Departement'), 'relations')
pvs.tag_object_of(('*', 'departement', 'Departement'), 'relations')
pvs.tag_object_of(('*', 'ar_in_departement', 'Departement'), 'hidden')
### XXX Costly pv_ctl.tag_object_of(('*', 'departement', 'Departement'), {'vid': 'table'})
# Commune
pvs.tag_subject_of(('Commune', 'in_region', 'Region'), 'attributes')
pvs.tag_object_of(('*', 'commune', 'Commune'), 'relations')
pv_ctl.tag_object_of(('*', 'commune', 'Commune'), {'vid': 'table'})
# Circonscription
pvs.tag_subject_of(('Circonscription', 'departement', 'Departement'), 'attributes')
pvs.tag_object_of(('*', 'circonscription', 'Circonscription'), 'relations')
pv_ctl.tag_object_of(('*', 'circonscription', 'Circonscription'), {'vid': 'table'})


### FACETS ####################################################################
class CommuneAreaFacet(facet.RangeFacet):
    __regid__ = 'commune-area-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Commune')
    order = 0
    rtype = 'area'


class CommuneDepartementFacet(facet.RelationFacet):
    __regid__ = 'commune-departement-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Commune')
    rtype = 'in_departement'
    target_attr = 'name'


class CirconscriptionDepartementFacet(facet.RelationFacet):
    __regid__ = 'circonscription-departement-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Circonscription')
    rtype = 'departement'
    target_attr = 'name'


class CirconscriptionAnneeFacet(facet.RelationFacet):
    __regid__ = 'circonscription-annee-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Circonscription')
    rtype = 'scrutin'
    target_attr = 'annee'


class DepartementRegionFacet(facet.RelationFacet):
    __regid__ = 'departement-region-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Departement')
    rtype = 'in_region'
    target_attr = 'name'


class CandidatureScrutinAnneeFacet(facet.RelationFacet):
    __regid__ = 'candidature-scrutin-annee-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Candidature')
    rtype = 'scrutin'
    target_attr = 'annee'


class CandidatureScrutinTypeFacet(facet.RelationFacet):
    __regid__ = 'candidature-scrutin-type-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Candidature')
    rtype = 'scrutin'
    target_attr = 'type'


class CandidatureEtiquetteFacet(facet.RelationFacet):
    __regid__ = 'candidature-etiqutte-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Candidature')
    rtype = 'etiquette'
    target_attr = 'nom'


class ListeDepartementFacet(facet.RQLPathFacet):
    __regid__ = 'liste-departement-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Liste')
    path = ['X commune C', 'C in_departement E', 'E name EN']
    filter_variable = 'EN'
    title = _('Departement')


class CandidatSexeFacet(facet.AttributeFacet):
    __regid__ = 'candidat-sexe-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Candidat')
    order = 1
    rtype = 'sexe'


class CandidatEtiquetteFacet(facet.RQLPathFacet):
    __regid__ = 'candidat-etiquette-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Candidat')
    path = ['C is Candidature', 'C etiquette E', 'E nom EN', 'C candidat X']
    order = 2
    filter_variable = 'EN'
    title = _('Etiquette')


class CandidatScrutinTypeFacet(facet.RQLPathFacet):
    __regid__ = 'candidat-scrutin-type-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Candidat')
    path = ['C candidat X', 'C scrutin T', 'T type TY']
    order = 2
    filter_variable = 'TY'
    title = _('Scrutin Type')


class CandidatScrutinAnneeFacet(facet.RQLPathFacet):
    __regid__ = 'candidat-scrutin-annee-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Candidat')
    path = ['C candidat X', 'C scrutin T', 'T annee TY']
    order = 2
    filter_variable = 'TY'
    title = _('Scrutin Annee')


class ScrutinTypeFacet(facet.AttributeFacet):
    __regid__ = 'scrutin-type-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Scrutin')
    rtype = 'type'


class ScrutinAnneeFacet(facet.AttributeFacet):
    __regid__ = 'scrutin-annee-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Scrutin')
    rtype = 'annee'


class TourScrutinTypeFacet(facet.RQLPathFacet):
    __regid__ = 'tour-scrutin-type-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Tour')
    path = ['X scrutin T', 'T type TY']
    order = 2
    filter_variable = 'TY'
    title = _('Scrutin Type')


class TourScrutinAnneeFacet(facet.RQLPathFacet):
    __regid__ = 'tour-scrutin-annee-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Tour')
    path = ['X scrutin T', 'T annee TY']
    order = 2
    filter_variable = 'TY'
    title = _('Scrutin Annee')


class TourValeurFacet(facet.AttributeFacet):
    __regid__ = 'tour-valeur-facet'
    __select__ = facet.AttributeFacet.__select__ & is_instance('Tour')
    rtype = 'valeur'


class StatistiqueInscritsFacet(facet.RangeFacet):
    __regid__ = 'statistique-inscrits-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'inscrits'


class StatistiqueAbstentionsFacet(facet.RangeFacet):
    __regid__ = 'statistique-abstentions-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'abstentions'


class StatistiqueVotantsFacet(facet.RangeFacet):
    __regid__ = 'statistique-votants-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'votants'


class StatistiqueExprimesFacet(facet.RangeFacet):
    __regid__ = 'statistique-exprimes-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'exprimes'


class StatistiqueBlancsNulsFacet(facet.RangeFacet):
    __regid__ = 'statistique-blancs_nuls-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'blancs_nuls'


class StatistiqueFractionAbstentionsInscritsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-abstentions-inscrits-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_abstentions_inscrits'


class StatistiqueFractionVotantsInscritsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-votants-inscrits-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_votants_inscrits'


class StatistiqueFractionNulsInscritsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-nuls-inscrits-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_nuls_inscrits'


class StatistiqueFractionExprimesInscritsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-exprimes-inscrits-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_exprimes_inscrits'


class StatistiqueFractionExprimesVotantsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-exprimes-votants-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_exprimes_votants'


class StatistiqueFractionNulsVotantsFacet(facet.RangeFacet):
    __regid__ = 'statistique-fraction-nuls-votants-facet'
    __select__ = facet.RangeFacet.__select__ & is_instance('Statistique')
    rtype = 'fraction_nuls_votants'


class StatistiqueScrutinTypeFacet(facet.RQLPathFacet):
    __regid__ = 'statistique-scrutin-type-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Statistique')
    path = ['X tour T', 'T scrutin S', 'S type TY']
    filter_variable = 'TY'
    title = _('Scrutin Type')


class StatistiqueScrutinAnneeFacet(facet.RQLPathFacet):
    __regid__ = 'statistique-scrutin-annee-facet'
    __select__ = facet.RQLPathFacet.__select__ & is_instance('Statistique')
    path = ['X tour T', 'T scrutin S', 'S annee TY']
    filter_variable = 'TY'
    title = _('Scrutin Annee')


class StatistiqueTourFacet(facet.RelationFacet):
    __regid__ = 'statistique-tour-facet'
    __select__ = facet.RelationFacet.__select__ & is_instance('Statistique')
    rtype = 'tour'
    target_attr = 'valeur'
    title = _('Tour')


### STARTUP ####################################################################
class ElectionsIndexView(IndexView):

    def call(self, **kwargs):
        w = self.w
        w(u'<div class="well">')
        w(u'<h1>%s</h1>' % self._cw._(u'Bienvenue sur CubicWeb Elections !'))
        # Description
        w(u"L'Etat a publié sur le site <a href='http://www.data.gouv.fr'>data.gouv.fr</a> les données correspondantes aux différentes élections des dernières années. Ce site présente à l'internaute les résultats complets au niveau communale des élections présidentielles, législatives et municipales depuis 2002.")
        # Cubicweb
        w(u'<h4>%s</h4>' % self._cw._(u'Cubicweb'))
        w(u"<a href='http://www.cubicweb.org/'>CubicWeb</a> est un système de gestion de connaissances publié sous license libre LGPL. Il permet de déployer rapidement des applications Web de gestion de connaissances, à partir du schéma des données manipulées, et propose aussi un moteur de requête puissant, le RQL, permettant la fouille complexe des données en base. L'interface utilisateur de CubicWeb a été spécialement conçue pour laisser à l'utilisateur final toute latitude pour sélectionner puis présenter les données.")
        cubicweb_url = u'''En savoir plus sur Cubicweb:
        <a href="http://www.cubicweb.org/">http://www.cubicweb.org/</a>'''
        w(u'<br/><small>%s</small>' % cubicweb_url)
        # Data
        w(u'<h4>%s</h4>' % self._cw._(u'Informations sur les données'))
        w(u'Les données brutes, '
               u'sous <a href="http://www.data.gouv.fr/Licence-Ouverte-Open-Licence">'
               u'Licence Ouverte</a>')
        url = u'http://www.data.gouv.fr/fr/dataset/resultats-elections'
        cubicweb_url = u'''Voir les résultats des élections sur:
        <a href="%s">http://www.data.gouv.fr</a>''' % url
        w(u'<br/><small>%s</small>' % cubicweb_url)
        url = u'http://osm13.openstreetmap.fr/~cquest/openfla/export/LICENCE.txt'
        osm_url = u'''Les données viennent de <a href="%s">OpenStreetMap</a>''' % url
        w(u'<br/><small>%s</small>' % osm_url)
        w(u'</div>') # well
        # LISTINGS
        w(u'<div class="row">')
        for title, etypes in ((_('Scrutins'), ('Scrutin', 'Tour', 'Statistique')),
                              (_('Candidats'), ('Candidat', 'Liste', 'Etiquette', 'Candidature')),
                              (_('Localisations'), ('Commune', 'Circonscription', 'Departement')),):
            w(u'<div class="col-md-4">')
            w(u'<h2>%s</h2>' % self._cw._(title))
            for etype in etypes:
                if not self._cw.execute('Any COUNT(X) WHERE X is %s' % etype)[0][0]:
                    continue
                url = self._cw.build_url(rql='Any X WHERE X is %s' % etype)
                self.w(u'<a href="%s" class="btn btn-large btn-block btn-success" '
                       u'type="button">%s</a>' % (url, self._cw._(etype)))
            w(u'</div>')
        w(u'</div>') #row
        # RQL
        w(u'<h3>%s</h3>' % u'Quelques requêtes RQL')
        w(u'<p>%s</p>' % u'Nombre de candidatures par scrutin et par étiquette politique')
        w(u'<blockquote>')
        _rql = ('Any E, S, COUNT(R) GROUPBY E,S WHERE R is Resultat, '
                'R candidature C, C etiquette E, C scrutin S')
        url = self._cw.build_url(rql=_rql)
        w(u'<a href="%s">%s</a>'  % (url, _rql))
        w(u'</blockquote>')
        w(u'<p>%s</p>' % u"Les prénoms des candidats triés par nombre de candidatures")
        w(u'<blockquote>')
        _rql = ('Any N, COUNT(X) GROUPBY N ORDERBY 2 DESC WHERE X prenom N')
        url = self._cw.build_url(rql=_rql)
        w(u'<a href="%s">%s</a>'  % (url, _rql))
        w(u'</blockquote>')
        w(u'<p>%s</p>' % u"Les prénoms des candidats triés par nombre de candidatures et groupés par étiquettes")
        w(u'<blockquote>')
        _rql = ('Any N, NE, COUNT(X) GROUPBY N, NE ORDERBY 3 DESC WHERE X prenom N, C candidat X, C etiquette E, E nom NE')
        url = self._cw.build_url(rql=_rql)
        w(u'<a href="%s">%s</a>'  % (url, _rql))
        w(u'</blockquote>')
        w(u'<p>%s</p>' % u"Les 100 communes ayant le moins d'absentions (fraction abstentions/inscrits)")
        w(u'<blockquote>')
        _rql = ('Any C, F, S, T ORDERBY F LIMIT 100 WHERE S commune C, '
                'S fraction_abstentions_inscrits F, S tour T')
        url = self._cw.build_url(rql=_rql)
        w(u'<a href="%s">%s</a>'  % (url, _rql))
        w(u'</blockquote>')
        w(u'<p>%s</p>' % u"Carte des 1000 communes ayant le moins d'absentions (fraction abstentions/inscrits) pour la présidentielle de 2012")
        w(u'<blockquote>')
        _rql = (u'Any ST_ASGEOJSON(G),  F LIMIT 1000 WHERE S commune C, C geometry G, '
                u'S fraction_abstentions_inscrits F, S tour T, T valeur 2, T scrutin SU, '
                u'SU annee 2012, SU type "présidentiel"')
        url = self._cw.build_url(rql=_rql, vid='leaflet-geojson')
        w(u'<a href="%s">%s</a>'  % (url, _rql))
        w(u'</blockquote>')
        # Utilisation
        w(u'Le modèle de donnée est exposé ici: '
          u'<a href="%(b)sschema">%(b)sschema</a>.</br>' % {'b': self._cw.base_url()})


### MAPS ######################################################################
class CandidatureMapView(EntityView):
    __regid__ = 'map'
    __select__ = EntityView.__select__ & is_instance('Candidature')
    paginable = False

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        attr = self._cw.form.get('__value', 'voix')
        rset = self._cw.execute('Any ST_ASGEOJSON(G), V WHERE X %(a)s V, '
                                'X candidature C, X commune CO, CO geometry G, '
                                'C eid %%(e)s' % {'a': attr}, {'e': entity.eid})
        self.wview('leaflet-geojson', rset=rset, custom_settings={'initialZoom': 16,
                                                                  'height': '800px'})


class DiffCandidatureMapView(EntityView):
    __regid__ = 'diffmap'
    __select__ = EntityView.__select__ & is_instance('Candidature') & multi_lines_rset(2)
    paginable = False

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        attr = self._cw.form.get('__value', 'voix')
        rset = self._cw.execute('Any ST_ASGEOJSON(G), V1-V2 WHERE '
                                'X1 %(a)s V1, X1 candidature C1, X1 commune CO, '
                                'X2 %(a)s V2, X2 candidature C2, X2 commune CO, '
                                'CO geometry G, C1 eid %%(e1)s, C2 eid %%(e2)s'
                                % {'a': attr}, {'e1': self.cw_rset[0][0],
                                                'e2': self.cw_rset[1][0]})
        self.wview('leaflet-geojson', rset=rset, custom_settings={'initialZoom': 16,
                                                                  'height': '800px'})

class StatistiqueMapView(EntityView):
    __regid__ = 'map'
    __select__ = EntityView.__select__ & is_instance('Statistique')
    paginable = False

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        attr = self._cw.form.get('__value', 'inscrits')
        rset = self._cw.execute('Any ST_ASGEOJSON(G), V WHERE '
                                'X %(a)s V, X commune CO, '
                                'CO geometry G, X eid %%(e1)s'
                                % {'a': attr}, {'e1': self.cw_rset[0][0]})
        self.wview('leaflet-geojson', rset=rset, custom_settings={'initialZoom': 16,
                                                                  'height': '800px'})



### REGISTRATION CALLBACK #####################################################
def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (ElectionsIndexView,))
    vreg.register_and_replace(ElectionsIndexView, IndexView)
    # Remove unused facets
    from cubicweb.web.views.facets import (CWSourceFacet, CreatedByFacet,
                                           InStateFacet, InGroupFacet,
                                           ETypeFacet, HasTextFacet)
    vreg.unregister(CWSourceFacet)
    vreg.unregister(CreatedByFacet)
    vreg.unregister(InStateFacet)
    vreg.unregister(InGroupFacet)
    vreg.unregister(ETypeFacet)
    vreg.unregister(HasTextFacet)
