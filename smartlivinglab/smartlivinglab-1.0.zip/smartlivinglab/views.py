import datetime

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework import status
from rest_framework import authentication
from smartlivinglab.models import Node, Sensor, Value
from smartlivinglab.serializers import NodeSerializer, SensorSerializer, SensorLinkSerializer
from django.views.decorators.csrf import ensure_csrf_cookie


class NodeList(generics.ListAPIView):
    """
    Returns a list of all nodes in the system.

    A node is a collection of sensors
    
    """
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class NodeDetail(generics.RetrieveAPIView):
    """
    Returns all attributes of a node.
    """
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class SensorList(generics.ListAPIView): 
    """
    Returns a list of all sensors in the system.

    A sensor is a collection of values
    
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorLinkSerializer

class SensorDetail(generics.RetrieveAPIView):
    """
    Return all atributes of a sensor
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class ValueView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, format=None):
        
        sensor = Sensor.objects.filter(code=request.DATA.get('sensor'))
        if not sensor.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            sensor = sensor[0]
        d = request.DATA.get('date')
        if d == None:
            d = datetime.datetime.utcnow()
        else:
            d = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        if sensor.clusterdeltatime > 0:
            minutes = d.minute
            delta = sensor.clusterdeltatime
            minutesdelta = minutes/delta * delta
            newdstring ="{0}-{1}-{2} {3}:{4:02d}:00".format(d.year, d.month, d.day, d.hour, minutesdelta)
            newd = datetime.datetime.strptime(newdstring, "%Y-%m-%d %H:%M:%S")
            v = Value.objects.filter(date = newd, sensor=sensor)
            if not v.exists():
                v = Value.objects.create(sensor=sensor,
                                         value=1,
                                         date=newd)
            else:
                v = v[0]
                v.value += 1
                v.save()
        else:    
            value = request.DATA.get('value')
            if value == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Value.objects.create(sensor=sensor,
                                 value=value,
                                 date=d)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'Nodes': reverse('node-list', request=request, format=format),
        'Sensors': reverse('sensor-list', request=request, format=format),
        })


    
