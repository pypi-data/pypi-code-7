from django_eulasees import models, serializers

from rest_framework import generics


class RawEulaList(generics.ListCreateAPIView):
    queryset = models.RawEula.objects.all()
    serializer_class = serializers.RawEulaSerializer


class RawEulaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.RawEula.objects.all()
    serializer_class = serializers.RawEulaSerializer
