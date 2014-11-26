# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-subprocess views/forms for web ui"""

import shlex
import json

from cubicweb.web.formwidgets import TextInput


class CmdlineInput(TextInput):
    def process_field_data(self, form, field):
        """Return process posted value(s) for widget and return a dumped form
        of the command line."""
        val = super(CmdlineInput, self).process_field_data(form, field)
        try:
            val = json.dumps(shlex.split(val))
        except (ValueError, TypeError):
            pass
        return unicode(val)

    def typed_value(self, form, field):
        """return field's *typed* value."""
        val = super(CmdlineInput, self).typed_value(form, field)
        try:
            val = u' '.join(json.loads(val))
        except (ValueError, TypeError):
            pass
        return unicode(val or u'')
