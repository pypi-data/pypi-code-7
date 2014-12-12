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

"""cubicweb-elections entity's classes"""


from cubicweb.entities import AnyEntity


class Tour(AnyEntity):
    __regid__ = 'Tour'

    def dc_title(self):
        return 'Tour %s (%s)' % (self.valeur, self.scrutin[0].dc_title())


class Candidat(AnyEntity):
    __regid__ = 'Candidat'
    fetch_attrs = ('sexe', 'prenom', 'nom')

    def dc_title(self):
        gender = 'Mr' if self.sexe == 'M' else 'Mme'
        return '%s %s %s' % (gender, self.prenom, self.nom)


class Candidature(AnyEntity):
    __regid__ = 'Candidature'

    def dc_title(self):
        title = self.candidat[0].dc_title()
        if self.etiquette:
            title += ' - %s' % self.etiquette[0].dc_title()
        title += ' (%s)' % self.scrutin[0].dc_title()
        return title


class Scrutin(AnyEntity):
    __regid__ = 'Scrutin'

    def dc_title(self):
        return 'Scrutin %s - %s' % (self.type, self.annee)


class Resultat(AnyEntity):
    __regid__ = 'Resultat'

    def dc_title(self):
        return u'Resultat - %s - %s - %s' % (self.candidature[0].candidat[0].dc_title(),
                                             self.commune[0].dc_title(),
                                             self.candidature[0].scrutin[0].dc_title())


class Circonscription(AnyEntity):
    __regid__ = 'Circonscription'

    def dc_title(self):
        return '%s %s (%s)' % (self.commune[0].dc_title(),
                               self.code,
                               self.scrutin[0].dc_title())


class Statistique(AnyEntity):
    __regid__ = 'Statistique'

    def dc_title(self):
        return u'Statistique - %s - %s' % (self.commune[0].dc_title(),
                                           self.tour[0].dc_title())
