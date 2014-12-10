from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_list_or_404, get_object_or_404
from smartlivinglab.models import Node, Sensor, Value
from django.db.models import Max

    
def index(request):
    h = {}
    h['sensors'] = Sensor.objects.all().annotate(Max('values__date')).order_by('code')
    return render_to_response('openlivinglab/samples/index.html', h, context_instance=RequestContext(request))

def sensor_index(request,sensor_code):
    h = {}
    h['sensor'] = get_object_or_404(Sensor, code=sensor_code)
    h['values'] = Value.objects.filter(sensor=h['sensor']).order_by('-id',)[:1000]
    h['values'] = list(h['values'])
    h['values'].reverse()
    return render_to_response('openlivinglab/samples/sensor_index.html', h, context_instance=RequestContext(request))
