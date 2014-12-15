# -*- coding: utf-8 -*-
'''
Taken from: http://www.djangosnippets.org/snippets/154/

Thanks to zakj.
'''
import json
from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse


class HttpJsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = json.dumps(
                object, cls=json.DjangoJSONEncoder, ensure_ascii=False)
        super(HttpJsonResponse, self).__init__(
            content, content_type='application/json')
