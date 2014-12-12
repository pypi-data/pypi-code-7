from __future__ import unicode_literals

from ..base import Resource

class AccommodationDossier(Resource):
    _resource_name = 'accommodation_dossiers'
    is_listable = True

    _as_is_fields = ['id', 'href', 'name', 'website']
