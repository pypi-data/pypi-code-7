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

class TagEulaList(generics.ListCreateAPIView):
    queryset = models.TagEula.objects.all()
    serializer_class = serializers.TagEulaSerializer

class TagIconList(generics.ListCreateAPIView):
    queryset = models.TagIcon.objects.all()
    serializer_class = serializers.TagIconSerializer

class SnippetTagList(generics.ListCreateAPIView):
    queryset = models.SnippetTag.objects.all()
    serializer_class = serializers.SnippetTagSerializer


class SnippetsForEula(generics.ListAPIView):
    serializer_class = serializers.EulaSnippetSerializer

    def get_queryset(self):

        pk = self.kwargs.get('pk')

        # get the eula
        eula = models.RawEula.objects.get(pk=pk)

        # Return the eula snippets
        return eula.eulasnippet_set.all()

class TagsForSnippet(generics.ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        # get the snippet
        snippet = models.EulaSnippet.objects.get(pk=pk)

        # get the tags for all tags associated with this snippet
        return [st.tag for st in snippet.snippettag_set.all()]
    
    

class TagsForEula(generics.ListAPIView):
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        # get the EULA
        eula = models.RawEula.objects.get(pk=pk)

        tags = set()
        results = []

        # loop round snippets for the EULA
        for snippet in eula.eulasnippet_set.all():
            # loop round snippettag's for the snippet
            for tag in snippet.snippettag_set.all():
                if tag.tag.pk not in tags:
                    tags.add(tag.tag.pk)
                    results.append(tag.tag)
            
        return results

class EulasForTag(generics.ListAPIView):
    serializer_class = serializers.RawEulaSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        tag = models.Tag.objects.get(pk=pk)

        eulas = set()
        results = []
        for snippet_tag in tag.snippettag_set.all():
            eid = snippet_tag.snippet.eula.pk
            if eid not in eulas:
                eulas.add(eid)
                results.append(snippet_tag.snippet.eula)
        
        return results
    
