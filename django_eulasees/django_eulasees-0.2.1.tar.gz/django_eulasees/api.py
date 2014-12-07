from django_eulasees import models, serializers

from rest_framework import generics


class RawEulaList(generics.ListCreateAPIView):
    queryset = models.RawEula.objects.all()
    serializer_class = serializers.RawEulaSerializer


class RawEulaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.RawEula.objects.all()
    serializer_class = serializers.RawEulaSerializer


class EulaSnippetList(generics.ListCreateAPIView):
    queryset = models.EulaSnippet.objects.all()
    serializer_class = serializers.EulaSnippetSerializer

class TagList(generics.ListCreateAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

class SnippetTagList(generics.ListCreateAPIView):
    queryset = models.SnippetTag.objects.all()
    serializer_class = serializers.SnippetTagSerializer


class SnippetsForEula(generics.ListAPIView):
    serializer_class = serializers.EulaSnippetSerializer

    def get_queryset(self):

        pk = self.kwargs.get('pk')

        eula = models.RawEula.objects.get(pk=pk)
    
        return eula.eulasnippet_set.all()

class TagsForSnippet(generics.ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = self.kwargs.get('pk')

        snippet = models.EulaSnippet.objects.get(pk=pk)
    
        return snippet.snippettag_set.all()
    

class TagsForEula(generics.ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = self.kwargs.get('pk')

        eula = models.RawEula.objects.get(pk=pk)
        
        eula.eulasnippet_set.all()
        
        snippet = models.EulaSnippet.objects.get(pk=pk)
    
        return snippet.snippettag_set.all()
