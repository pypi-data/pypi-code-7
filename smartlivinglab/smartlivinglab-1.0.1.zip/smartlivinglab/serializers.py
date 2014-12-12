from rest_framework import serializers
from rest_framework import pagination
from smartlivinglab.models import Node, Sensor, Value
from django.core.paginator import Paginator

class NodeSerializer(serializers.HyperlinkedModelSerializer):
    sensors = serializers.HyperlinkedRelatedField(many=True, view_name='sensor-detail')

    class Meta:
        model = Node
        fields = ('url','code','description','lat','lon','sensors') 


class ValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Value
        fields = ('date', 'value')
        
class ValuePaginatedSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = ValueSerializer

class SensorLinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sensor
        values = ('node','id','units','code')
        
class SensorSerializer(serializers.HyperlinkedModelSerializer):
    values = serializers.SerializerMethodField('paginated_values')
    
    class Meta:
        model = Sensor
        fields = ('node','id','units', 'code', 'values')

    def paginated_values(self, obj):
        paginator = Paginator(obj.values.all().order_by('-pk'), 100)
        request = self.context['request']
        if 'page' in request.QUERY_PARAMS.keys():
            pagenumber = int(request.QUERY_PARAMS.get('page'))
        else:
            pagenumber = 1
        values = paginator.page(pagenumber)
        serializer = ValuePaginatedSerializer(values, context={'request': request})
        return serializer.data
