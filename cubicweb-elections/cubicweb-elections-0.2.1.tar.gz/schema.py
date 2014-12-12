# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-scrutins schema"""
from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
			    String, Int, Float, Date)
from cubicweb.schemas.base import ExternalUri

from cubes.postgis.schema import Geometry


###############################################################################
### CANDIDAT ##################################################################
###############################################################################
class Candidat(EntityType):
    nom = String(required=True, fulltextindexed=True, indexed=True, maxsize=64)
    prenom = String(fulltextindexed=True, maxsize=64)
    sexe = String(indexed=True, vocabulary=('M','F'))


class Etiquette(EntityType):
    nom = String(indexed=True, fulltextindexed=True, maxsize=256)


class Candidature(EntityType):
    candidat = SubjectRelation('Candidat', cardinality='1*', inlined=True)
    scrutin = SubjectRelation('Scrutin', cardinality='1*', inlined=True)
    etiquette = SubjectRelation('Etiquette', cardinality='?*', inlined=True)
    liste = SubjectRelation('Liste', cardinality='?*', inlined=True)
    circonscription = SubjectRelation('Circonscription', cardinality='?*', inlined=True)


class Liste(EntityType):
    nom = String(required=True, fulltextindexed=True, indexed=True, maxsize=256)
    commune = SubjectRelation(('Commune', 'Secteur'), cardinality='1*', inlined=True)


###############################################################################
### SCRUTINS #################################################################
###############################################################################
class Scrutin(EntityType):
    type = String(required=True, maxsize=256)
    annee = Int(required=True)

class Tour(EntityType):
    valeur = Int(required=True)
    scrutin = SubjectRelation('Scrutin', cardinality='1*', inlined=True)


class Resultat(EntityType):
    voix = Int(indexed=True)
    sieges = Int(indexed=True)
    fraction_voix_inscrits = Float(indexed=True)
    fraction_voix_exprimes = Float(indexed=True)
    tour = SubjectRelation('Tour', cardinality='1*', inlined=True)
    candidature = SubjectRelation('Candidature', cardinality='1*', inlined=True)
    departement = SubjectRelation('Departement', cardinality='1*', inlined=True)
    commune = SubjectRelation(('Commune', 'Secteur'), cardinality='1*', inlined=True)
    circonscription = SubjectRelation('Circonscription', cardinality='?*', inlined=True)


class Statistique(EntityType):
    inscrits = Int(indexed=True)
    abstentions = Int(indexed=True)
    fraction_abstentions_inscrits = Float(indexed=True)
    votants = Int(indexed=True)
    fraction_votants_inscrits = Float(indexed=True)
    blancs_nuls = Int(indexed=True)
    fraction_nuls_inscrits = Float(indexed=True)
    fraction_nuls_votants = Float(indexed=True)
    exprimes = Int(indexed=True)
    fraction_exprimes_inscrits = Float(indexed=True)
    fraction_exprimes_votants = Float(indexed=True)
    commune = SubjectRelation(('Commune', 'Secteur'), cardinality='1*', inlined=True)
    tour = SubjectRelation('Tour', cardinality='1*', inlined=True)


###############################################################################
### GEOGRAPHY #################################################################
###############################################################################
class Secteur(EntityType):
    nom = String(indexed=True, fulltextindexed=True, maxsize=256)
    code = String(indexed=True, maxsize=16)
    commune = SubjectRelation('Commune', cardinality='1*', inlined=True)

class Circonscription(EntityType):
    # XXX Circonscription may changed across year
    code = Int(indexed=True)
    scrutin = SubjectRelation('Scrutin', cardinality='1*', inlined=True)
    departement = SubjectRelation('Departement', cardinality='?*', inlined=True)
    commune = SubjectRelation('Commune', cardinality='1*', inlined=True)
