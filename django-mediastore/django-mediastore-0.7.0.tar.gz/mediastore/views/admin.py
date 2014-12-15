from django.template import RequestContext
from django.shortcuts import render_to_response


def add(request):
    is_popup = request.GET.get('_is_popup', 1)
    return render_to_response('admin/mediastore/add_select.html', {
        'is_popup': is_popup,
    }, context_instance=RequestContext(request))
