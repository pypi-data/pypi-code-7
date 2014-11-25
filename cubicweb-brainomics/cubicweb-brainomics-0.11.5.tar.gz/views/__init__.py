# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
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

"""cubicweb-suivimp views/forms/actions/components for web ui"""
from logilab.common.decorators import monkeypatch

from cubicweb.web.views import basetemplates
from cubicweb.web.views import uicfg


###############################################################################
### UICFG MODIFICATIONS #######################################################
###############################################################################
uicfg.primaryview_display_ctrl._relrsetdefs = {}
uicfg.primaryview_display_ctrl._attrrsetdefs = {}

@monkeypatch(uicfg.DisplayCtrlRelationTags)
def __init__(self, *args, **kwargs):
    super(DisplayCtrlRelationTags, self).__init__(*args, **kwargs)
    self.counter = 0
    self._attrrsetdefs = {}
    self._relrsetdefs = {}

@monkeypatch(uicfg.DisplayCtrlRelationTags)
def display_rset(self, etype, section, props):
    """
    The display_rset method of uicfg take 3 arguments:

        * the name of the etype concerned by the rule;

        * the section where the information is displayed (attributes or relations);

        * a dictionnary of properties.

    The dictionnary of properties must have:

       * a 'callback' item OR a 'rql' and a 'vid' items.

    The 'callback' is a function that takes the entity and render an HTML snipet.

    The 'rql' is a rql query where the variable 'X' is the current entity. The 'vid'
    is the __regid__ of the view that will be applied to the result of the rql query.

    It could also have:

       * a 'label' ('' if not given);

       * an 'order' (9999 if not given);

    It should be used as follows, e.g. using an etype property:

      >>> _pvdc = uicfg.primaryview_display_ctrl
      >>> _pvdc.display_rset('MyEtype', 'attributes',
                             {'callback': lambda x: x.formatted_description,
                              'label': _('description')})

    or with a 'rql' and 'vid' attributes (in this case 'X' is the current entity):

      >>> _pvdc = uicfg.primaryview_display_ctrl
      >>> _pvdc.display_rset('MyEtype', 'relations',
                             {'rql': 'Any Z WHERE X relation1 Y, Y relation2 Z',
                              'vid': 'my-view',
                              'label': _('My label')})

    or with a 'callback' using a view:


      >>> _pvdc = uicfg.primaryview_display_ctrl
      >>> _pvdc.display_rset('MyEtype', 'relations',
                             {'callback': lambda x: x.view('my-secondary-view'),
                             'order': 2,
                             'label': _('My label')})

    """
    assert ('rql' in props and 'vid' in props) or 'callback' in props
    if section == 'attributes':
        self._attrrsetdefs.setdefault(etype, []).append(props)
    elif section == 'relations':
        self._relrsetdefs.setdefault(etype, []).append(props)
    else:
        self.warning('display_rset for %s should be in section '
                     '"attributes" or "relations"' % etype)

