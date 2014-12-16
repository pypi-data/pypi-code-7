# -*- coding: utf-8 -*-

import json

from django.views.decorators.cache import never_cache
from django.http import HttpResponse

from proxylist import now


@never_cache
def mirror(request):
    start = now()

    serializable = (str, unicode, bool, int, float)

    output = dict()

    output['REMOTE_ADDR'] = request.META.get('REMOTE_ADDR', '')
    output['REMOTE_HOST'] = request.META.get('REMOTE_HOST', '')

    # HTTP Headers
    output['http_headers'] = dict()
    for k, v in request.META.items():
        if k.startswith('HTTP_') and type(v) in serializable:
            output['http_headers'][k[5:]] = v

    # Timing
    output['response_start'] = str(start)
    output['response_end'] = str(now())

    return HttpResponse(json.dumps(output))
